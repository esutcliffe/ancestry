# Pentimenti → GitHub Pages migration

## Decision
Serve the whole family site from this repo on GitHub Pages, then point **pentimenti.org** at GitHub Pages so old URLs keep working.

**Homepage:** the Pentimenti intro letter to Brynn, Carly, and Fallon (`index.html`).
**Key subpage:** printable branching trees at `/tree` (`tree/index.html` or `tree.html`).

## Rollback / Network Solutions
**Copy only.** Leave every Network Solutions Website Builder page and file in place. Do not delete, unpublish, or replace the NS originals. If we need to reverse the cutover, point DNS for `pentimenti.org` back to Network Solutions — the old site should still be there.

## Order of operations
1. Copy pages into this repo on `site-migration` (paths matching today’s pentimenti.org URLs).
2. ~~Move today’s tree `index.html` → `/tree`, copy the intro letter to `index.html`, and point the homepage CTA at `/tree`.~~ **Done** (`tree/index.html` + letter at `/`).
3. Retarget internal links (and the tree’s person links) to local paths (tree person cards now use local `../sutcliffe|riley|bock/.../` paths).
4. Preview on the branch / Pages preview.
5. Merge to `working`.
6. Add the custom domain in GitHub Pages settings + DNS at Network Solutions.
7. Only then flip DNS — do **not** point the domain before the paths exist here.

## URL inventory
See `_migration/sitemap-urls.txt` (from https://pentimenti.org/sitemap.xml, ~70 URLs).

### Already in this repo
- `index.html` — Pentimenti intro letter homepage (from live pentimenti.org)
- `tree/index.html` — printable branching trees
- `sutcliffe/`, `riley/`, `bock/` — person/lawsuit/letter pages copied from live pentimenti.org
- `sutcliffe/carl_theodor_hansen.html`, `sutcliffe/carl_leonard_nelson.html` — older SingleFile dumps
- `sutcliffe/letters/*` — WWI letter chapter dumps + menu

### Still only on Network Solutions Website Builder
`/ancestry/` builder-squeezed tree (skip), privacy policy, and anything not listed in `_migration/sitemap-urls.txt` as copied.

## Target path mapping
| Live today | In this repo |
|---|---|
| `/` | intro letter → `index.html` |
| trees (GitHub today) | `/tree` |
| `/ancestry/` | builder-squeezed tree; skip migrating this copy — leave it on NS |
| `/sutcliffe/.../` | `sutcliffe/.../index.html` |
| `/riley/.../` | `riley/.../index.html` |
| `/bock/.../` | `bock/.../index.html` |

## Notes
- Website Builder cannot host a true standalone tree; that is why GitHub is home.
- Prefer clean exported HTML over another round of 1MB+ SingleFile dumps when practical.
- DNS for apex `pentimenti.org` will need GitHub Pages A/ALIAS records at Network Solutions; `www` can CNAME to `esutcliffe.github.io`.
