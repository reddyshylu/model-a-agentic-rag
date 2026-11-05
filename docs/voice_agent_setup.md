# Emergency voice agent setup (ElevenLabs Agents + Twilio)

All data is fictional. The agent calls ONLY your own verified phone, which plays the
"hospital nurse line" in the demo. Never configure 911 or a real hospital number.

## 1. Twilio
1. Create a Twilio trial account and buy a phone number.
2. Verify your own mobile number in Twilio (trial accounts can only call verified numbers,
   which is an extra safety net for the demo).

## 2. ElevenLabs agent
Quick way: put ELEVENLABS_API_KEY and ELEVENLABS_VOICE_ID in .env, then run
`python scripts/create_emergency_agent.py` (add `--dry-run` first to see the request). It creates the agent
below with recording off, and prints the agent id. The manual dashboard steps are the same settings:

1. Create an agent named "Model A emergency caller".
2. Phone Numbers: import your Twilio number (Account SID and Auth Token), assign this agent.
   Copy the phone number id into `ELEVENLABS_PHONE_NUMBER_ID`.
3. Copy the agent id into `ELEVENLABS_AGENT_ID`.
4. First message:

   > This is an automated urgent alert from Model A for the LiverWell care team. Alert {{alert_id}}.
   > Patient {{patient_ref}} reported: {{alert_reason}}, at {{alert_time}}. The patient has been told
   > to call 911 or go to the emergency room. Can you confirm you received this alert?

5. System prompt:

   > You are an automated alert caller for a liver clinic demo. You speak to a care-team member.
   > Your only job: deliver the alert in the first message, answer questions using only the alert
   > details ({{alert_id}}, {{patient_ref}}, {{alert_reason}}, {{alert_time}}), and get a clear
   > confirmation that the alert was received. You have no other patient information. Do not give
   > medical advice. If asked anything you do not know, say the details are in the clinician queue
   > and the clinic callback number is {{callback_number}}. Repeat the alert if asked. When the
   > listener confirms, thank them and end the call. Always say you are an automated system if asked.

6. Analysis > Data collection: add a boolean field `acknowledged`, described as
   "True only if the listener clearly confirmed they received the alert."
7. Turn call recording off. Turn voicemail detection on if your plan offers it.
8. Webhooks: enable the post-call webhook (transcription and call initiation failure) pointing to
   `https://<your tunnel>/elevenlabs/post-call`, and copy the secret into `ELEVENLABS_WEBHOOK_SECRET`.

## 3. Model A `.env`
```
VOICE_MODE=dry_run                       # switch to live only after the dry run looks right
VOICE_CARE_TEAM_NUMBER=+1XXXXXXXXXX      # your own verified phone
VOICE_ALLOWED_NUMBERS=+1XXXXXXXXXX       # same number; anything else is refused
```

## 4. Test in this order
1. Use the agent's built-in test call in the ElevenLabs dashboard.
2. `python scripts/test_call.py --patient P20` with `VOICE_MODE=dry_run`: check `data/escalations/calls.jsonl`.
3. Set `VOICE_MODE=live`, run the same script: your phone should ring.
4. Start `uvicorn scripts.voice_webhook:app --port 8080` behind a tunnel, answer and confirm:
   the escalation becomes `acknowledged_by_phone`. Let it ring out: it retries once, then is
   flagged `unacknowledged`.

## What the call carries
alert id, fictional MRN (LW-xxxxxxx), reason (the red-flag words), time, clinic callback number.
No labs, no diagnosis, no name, no recording.
