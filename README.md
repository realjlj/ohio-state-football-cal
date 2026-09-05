# Ohio State Football calendar (scores in titles)

Live iCal feed mirrored from Ohio State's official Sidearm calendar, with event titles rewritten so final scores show in the title (e.g. `W 56-3 · vs Ball State`).

## Subscribe (Apple Calendar / Google / Outlook)

Prefer jsDelivr (GitHub raw CDN can lag):

**webcal:**

```
webcal://cdn.jsdelivr.net/gh/realjlj/ohio-state-football-cal@main/ohio-state-football.ics
```

**https:**

```
https://cdn.jsdelivr.net/gh/realjlj/ohio-state-football-cal@main/ohio-state-football.ics
```

Fallback (may take a few minutes to update after a publish):

```
https://raw.githubusercontent.com/realjlj/ohio-state-football-cal/main/ohio-state-football.ics
```

Mac: Calendar → File → New Calendar Subscription… → paste the webcal URL → refresh hourly.

iPhone: Settings → Apps → Calendar → Accounts → Add Account → Other → Add Subscribed Calendar.

Remove any earlier official `ohiostatebuckeyes.com` football subscription and the one-shot `.ics` import so you don't get duplicates.

## Source

Upstream: `https://ohiostatebuckeyes.com/calendar.ashx/calendar.ics?sport_id=2`

`rewrite_osu_ics.py` regenerates `ohio-state-football.ics`. A Grok Bot routine refreshes it through the season.
