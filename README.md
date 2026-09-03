# Cyclist Companion — website

The public site for the Cyclist Companion app: privacy policy, support, and the
tyre pressure methodology. Served by GitHub Pages at <https://cc.velostables.com>.

The custom domain is set by the `CNAME` file in this directory:
`cc.velostables.com`. DNS lives in Cloudflare, and because this is a subdomain
rather than the apex it needs exactly **one** record:

| Type | Name | Content | Proxy |
| --- | --- | --- | --- |
| CNAME | `cc` | `thecooperx.github.io` | DNS only |

A subdomain is deliberate. The apex cannot hold a CNAME, so pointing
`velostables.com` itself at Pages meant four A records that have to be edited
by hand whenever GitHub changes an address, and it collided with the records
already serving the root domain. `cc` sidesteps both.

The root domain, its `www`, and the Microsoft 365 `MX` and SPF `TXT` records are
nothing to do with hosting this site. Leave them alone — the `MX` and `TXT`
records especially, or email breaks.

### If the site returns a Cloudflare error

**Both URLs break together, which is the confusing part.** The `CNAME` file
makes GitHub Pages 301-redirect `thecooperx.github.io/cyclist-companion-site/`
to the custom domain, so if the domain is misconfigured the github.io address
fails too — and the app's in-app links use the github.io form.

Ask GitHub directly, with the right `Host` header, before touching anything
here:

```bash
curl -s -o /dev/null -w '%{http_code}\n' -H 'Host: cc.velostables.com' \
  --insecure https://185.199.108.153/privacy/
```

If that returns 200 while the public URL does not, the fault is in DNS and no
amount of pushing to this repository will fix it. Check the `CNAME` record
above exists, points at `thecooperx.github.io` (not at this repository's URL),
and is set to **DNS only**. Proxying does work, but only with SSL/TLS mode
**Full**; on **Flexible** it produces a redirect loop.

This is how the apex failed on 2026-09-03: `velostables.com` resolved to
Cloudflare proxy addresses with something other than Pages behind them, and
served "Error. Page cannot be displayed" while GitHub was serving the site
perfectly well. Both public URLs failed together, because the `CNAME` file makes
GitHub redirect `thecooperx.github.io/cyclist-companion-site/` to the custom
domain.

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
