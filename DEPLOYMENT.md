# Deploy to Vercel

This project is configured for Vercel with FastAPI and a daily cron job.

## Cron schedule

Vercel cron schedules use UTC. The schedule in `vercel.json` is:

```cron
30 2 * * *
```

That runs every day at 02:30 UTC, which is 08:00 in India Standard Time.

## Required Vercel environment variables

Add these in Vercel Project Settings -> Environment Variables:

```env
DATABASE_URL=postgresql://USER:PASSWORD@HOST:5432/DB_NAME
GROQ_API_KEY=your_groq_api_key
SMTP_EMAIL=your_gmail_address@gmail.com
SMTP_PASSWORD=your_gmail_app_password
```

Use a hosted PostgreSQL database. `localhost` databases do not work from Vercel.

## Deploy commands

Install and login to Vercel:

```bash
npm i -g vercel
vercel login
```

Deploy preview:

```bash
vercel
```

Deploy production:

```bash
vercel --prod
```

The cron job is registered on the production deployment and calls:

```text
/send-mail
```
