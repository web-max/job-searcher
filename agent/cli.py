"""Command-line interface. Every command is safe to re-run; nothing sends."""
import argparse
import sys

from .settings import load_profile, load_settings


def cmd_gui(args):
    import sys as _sys
    from pathlib import Path
    _sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
    from gui.app import main as gui_main
    gui_main(port=args.port, open_browser=not args.no_browser)


def cmd_discover(args):
    from . import discover
    result = discover.run(load_profile(), load_settings())
    print(f"\nfetched {result['fetched']} postings "
          f"({', '.join(f'{k}: {v}' for k, v in result['per_source'].items())})")
    print(f"fresh: {result['fresh']}  kept after dealbreaker filter: {result['kept']}  "
          f"new in tracker: {result['new']}")


def cmd_rank(args):
    from . import rank
    result = rank.run(load_profile(), load_settings())
    print(f"\nranked {result['ranked']} jobs; {result['surfaced']} above the surface threshold")
    print("run: python -m agent report")


def cmd_report(args):
    from . import tracker
    settings = load_settings()
    min_score = settings.get("ranking", {}).get("min_score_to_surface", 65)
    vols = settings.get("volumes", {})

    print("=== Top matches (apply to these first) ===")
    jobs = tracker.top_jobs(min_score=min_score)
    if not jobs:
        print("  none yet - run discover + rank, or lower min_score_to_surface")
    for j in jobs:
        print(f"  [{j['score']:>3}] {j['id']}  {j['title']} @ {j['company']} "
              f"({j['location'] or 'location n/a'}) {j['posted_at']}")
        print(f"        {j['score_reason']}")
        print(f"        {j['url']}")

    print("\n=== Follow-ups due ===")
    due = tracker.followups_due(vols.get("followup_after_days", 6), vols.get("max_followups", 2))
    if not due:
        print("  none")
    for c in due:
        print(f"  {c['name']} ({c['role']} @ {c['company']}) - last touch {c['last_touch'][:10]}, "
              f"bumps so far: {c['bumps'] or 0}")
        print(f"    draft one: python -m agent outreach --kind followup --person \"{c['name']}\" --company \"{c['company']}\"")

    print("\n=== Pipeline ===")
    snap = tracker.pipeline_snapshot()
    print(f"  jobs: {snap['jobs'] or '{}'}")
    print(f"  contacts: {snap['contacts'] or '{}'}")
    counts = tracker.counts_today()
    print(f"  today: {counts['applied']} applications logged, {counts['messaged']} messages logged "
          f"(caps: {vols.get('max_applications_per_day')}/day apps, {vols.get('max_new_outreach_per_day')}/day outreach)")


def cmd_tailor(args):
    from . import tailor
    tailor.run(args.job)


def cmd_outreach(args):
    from . import outreach, tracker
    if args.person and not tracker.find_contact(args.person):
        tracker.add_contact(args.person, company=args.company or "", role=args.person_role or "",
                            relationship=args.relationship, job_id=args.job)
    outreach.draft(args.kind, person=args.person or "", person_role=args.person_role or "",
                   company=args.company or "", job_id=args.job, context=args.context or "",
                   channel=args.channel)


def cmd_voice_build(args):
    from . import voice
    profile = voice.build_profile()
    print(profile.split("## Real samples")[0])
    print(f"voice profile written to voice/voice_profile.md")


def cmd_lint(args):
    from . import humanize
    text = open(args.file).read() if args.file else sys.stdin.read()
    findings = humanize.lint(text, kind=args.kind)
    print(humanize.format_findings(findings))
    sys.exit(1 if humanize.blocking(findings) else 0)


def cmd_log(args):
    from . import tracker
    contact_id = None
    if args.contact:
        c = tracker.find_contact(args.contact)
        if not c:
            contact_id = tracker.add_contact(args.contact)
            print(f"created contact '{args.contact}'")
        else:
            contact_id = c["id"]
    tracker.log_event(args.event, job_id=args.job, contact_id=contact_id, detail=args.detail or "")
    print(f"logged: {args.event}" + (f" (job {args.job})" if args.job else "")
          + (f" (contact {args.contact})" if args.contact else ""))


def cmd_status(args):
    from . import tracker
    n = tracker.set_status(args.job, args.to)
    print("updated" if n else f"job {args.job} not found")


def main():
    p = argparse.ArgumentParser(prog="agent", description="Human-in-the-loop job search agent")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("gui", help="launch the local web app (opens in your browser)")
    sp.add_argument("--port", type=int, default=7333)
    sp.add_argument("--no-browser", action="store_true")

    sub.add_parser("discover", help="pull fresh jobs from all enabled sources")
    sub.add_parser("rank", help="LLM-score unranked jobs against the profile")
    sub.add_parser("report", help="top matches, follow-ups due, pipeline snapshot")

    sp = sub.add_parser("tailor", help="keyword gaps + bullets + cover note for one job")
    sp.add_argument("--job", required=True)

    sp = sub.add_parser("outreach", help="draft an outreach message into outbox/")
    sp.add_argument("--kind", required=True,
                    choices=["connection_note", "info_interview", "hiring_manager", "recruiter",
                             "referral_ask", "followup", "thank_you", "forwardable"])
    sp.add_argument("--person", help="recipient name")
    sp.add_argument("--person-role", dest="person_role", help="recipient's role")
    sp.add_argument("--company")
    sp.add_argument("--job", help="job id from the tracker")
    sp.add_argument("--context", help="specific research notes: their post, shared background, news")
    sp.add_argument("--channel", default="linkedin", choices=["linkedin", "email"])
    sp.add_argument("--relationship", default="employee",
                    choices=["employee", "hiring_manager", "recruiter", "mutual"])

    sub.add_parser("voice-build", help="build voice profile from voice/corpus/")

    sp = sub.add_parser("lint", help="lint a draft for AI tells (file or stdin)")
    sp.add_argument("--file")
    sp.add_argument("--kind", default="linkedin_message",
                    choices=["linkedin_note", "linkedin_message", "email", "cover_note"])

    sp = sub.add_parser("log", help="log an event after YOU did the thing")
    sp.add_argument("--event", required=True,
                    choices=["applied", "messaged", "followed_up", "replied", "call",
                             "rejected", "offer", "note"])
    sp.add_argument("--job")
    sp.add_argument("--contact")
    sp.add_argument("--detail")

    sp = sub.add_parser("status", help="set a job's status")
    sp.add_argument("--job", required=True)
    sp.add_argument("--to", required=True,
                    choices=["new", "ranked", "shortlisted", "applied", "interviewing",
                             "offer", "rejected", "dropped"])

    args = p.parse_args()
    {
        "gui": cmd_gui,
        "discover": cmd_discover, "rank": cmd_rank, "report": cmd_report,
        "tailor": cmd_tailor, "outreach": cmd_outreach, "voice-build": cmd_voice_build,
        "lint": cmd_lint, "log": cmd_log, "status": cmd_status,
    }[args.cmd](args)


if __name__ == "__main__":
    main()
