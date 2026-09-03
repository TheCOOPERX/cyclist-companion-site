# Cyclist Companion — website

The public site for the Cyclist Companion app: privacy policy, support, and the
tyre pressure methodology. Served by GitHub Pages at <https://velostables.com>.

The custom domain is set by the `CNAME` file in this directory. DNS lives in
Cloudflare: four A records on the apex pointing at GitHub's Pages addresses, and
`www` as a CNAME to `thecooperx.github.io`. The Microsoft 365 `MX` and SPF `TXT`
records are unrelated to hosting and must be left alone, or email breaks.

### If the site returns a Cloudflare error

**Both URLs break together, which is the confusing part.** The `CNAME` file
makes GitHub Pages 301-redirect `thecooperx.github.io/cyclist-companion-site/`
to the custom domain, so if the domain is misconfigured the github.io address
fails too — and the app's in-app links use the github.io form.

Checked 2026-09-03: `velostables.com` resolved to Cloudflare's proxy addresses
and returned "Error. Page cannot be displayed", while GitHub Pages served the
site correctly for that hostname:

```bash
curl -s -o /dev/null -w '%{http_code}\n' -H 'Host: velostables.com' \
  --insecure https://185.199.108.153/privacy/     # 200 — GitHub is fine
```

If that returns 200 while the public URL does not, the fault is in Cloudflare,
not in this repository, and no amount of pushing will fix it. In the Cloudflare
DNS tab:

| Type | Name | Content |
| --- | --- | --- |
| A | `velostables.com` | `185.199.108.153` |
| A | `velostables.com` | `185.199.109.153` |
| A | `velostables.com` | `185.199.110.153` |
| A | `velostables.com` | `185.199.111.153` |
| CNAME | `www` | `thecooperx.github.io` |

Delete any other `A` or `AAAA` record on the apex — a leftover parking record is
the usual cause. Set these to **DNS only** (grey cloud): proxying works, but
only with SSL/TLS mode **Full**, and on **Flexible** it produces a redirect
loop. Leave `MX` and `TXT` alone.

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
