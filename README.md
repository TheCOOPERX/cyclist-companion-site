# Cyclist Companion — website

The public site for the Cyclist Companion app: privacy policy, support, and the
tyre pressure methodology. Served by GitHub Pages.

The app's source lives in a separate private repository. Nothing here is
generated from it — these are hand-written static pages with no build step, no
JavaScript and no external requests.

## Pages

| Path | Purpose |
| --- | --- |
| `/` | Overview |
| `/privacy/` | Privacy policy — **required by App Store Connect** |
| `/support/` | Support and FAQ — **required by App Store Connect** |
| `/methodology/` | How the tyre pressure model works |

## Before submitting the app

Replace every occurrence of `SUPPORT_EMAIL_HERE` with a real, monitored address:

```bash
grep -rl SUPPORT_EMAIL_HERE . | xargs sed -i '' 's/SUPPORT_EMAIL_HERE/you@example.com/g'
```

App Review does check that a support URL resolves and offers a way to make
contact. A placeholder will not pass.

## Local preview

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000>.

## Notes

- `.nojekyll` is present so GitHub Pages serves the files as-is rather than
  running them through Jekyll.
- Keep the privacy policy honest. It currently claims the app makes no network
  requests and collects nothing, which is true of the shipping build. If a
  feature ever changes that — a weather lookup for temperature-adjusted pressure
  is the likeliest candidate — update this policy *before* that version ships.
- The methodology page deliberately documents the model's limits, including
  where it stops being valid above roughly 65 mm. Keep it in step with
  `lib/utils/pressure_math.dart` in the app repo.
