# Cyclist Companion — website

The public site for the Cyclist Companion app: privacy policy, support, and the
tyre pressure methodology. Served by GitHub Pages at <https://velostables.com>.

The custom domain is set by the `CNAME` file in this directory. DNS lives in
Cloudflare: four A records on the apex pointing at GitHub's Pages addresses, and
`www` as a CNAME to `thecooperx.github.io`. The Microsoft 365 `MX` and SPF `TXT`
records are unrelated to hosting and must be left alone, or email breaks.

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

## Contact address

The published support address is `support@velostables.com`, which appears once
on the privacy page and three times on the support page. To change it:

```bash
grep -rl support@velostables.com --include="*.html" . \
  | xargs sed -i '' 's/support@velostables\.com/new@example.com/g'
```

App Review checks that the support URL resolves and offers a route to make
contact, so this address needs to stay monitored.

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
