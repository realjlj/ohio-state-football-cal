# Ohio State Football calendar (scores in titles)

Live iCal feed mirrored from Ohio State's official Sidearm calendar, with event titles rewritten so final scores show in the title (e.g. `W 56-3 · vs Ball State`).

## Subscribe (Apple Calendar / Google / Outlook)

**webcal:**

```
webcal://raw.githubusercontent.com/realjlj/ohio-state-football-cal/main/ohio-state-football.ics
```

**https:**

```
https://raw.githubusercontent.com/realjlj/ohio-state-football-cal/main/ohio-state-football.ics
```

Mac: Calendar → File → New Calendar Subscription… → paste the webcal URL → refresh hourly.

iPhone: Settings → Apps → Calendar → Accounts → Add Account → Other → Add Subscribed Calendar.

Unsubscribe from the official `ohiostatebuckeyes.com` football feed if you added that earlier, so you don't get duplicates.

## Source

Upstream: `https://ohiostatebuckeyes.com/calendar.ashx/calendar.ics?sport_id=2`

`rewrite_osu_ics.py` regenerates `ohio-state-football.ics`. A Grok Bot routine keeps the file updated.
