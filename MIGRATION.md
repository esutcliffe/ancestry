# Pentimenti → GitHub Pages migration

## Decision
Serve the whole family site from this repo on GitHub Pages, then point **pentimenti.org** at GitHub Pages so old URLs keep working.

## Rollback / Network Solutions
**Copy only.** Leave every Network Solutions Website Builder page and file in place. Do not delete, unpublish, or replace the NS originals. If we need to reverse the cutover, point DNS for `pentimenti.org` back to Network Solutions — the old site should still be there.

## Order of operations
1. Copy pages into this repo on `site-migration` (paths matching today’s pentimenti.org URLs).
2. Retarget internal links (and the tree’s person links) to local paths.
3. Preview on the branch / Pages preview.
4. Merge to `working`.
5. Add the custom domain in GitHub Pages settings + DNS at Network Solutions.
6. Only then flip DNS — do **not** point the domain before the paths exist here.

## URL inventory
See `_migration/sitemap-urls.txt` (from https://pentimenti.org/sitemap.xml, ~70 URLs).

### Already in this repo
- `index.html` — printable branching trees (canonical good copy)
- `sutcliffe/carl_theodor_hansen.html`, `sutcliffe/carl_leonard_nelson.html` — older SingleFile dumps
- `sutcliffe/letters/*` — WWI letter chapter dumps + menu

### Still only on Network Solutions Website Builder
Most person bios, branch hubs, homepage letter, lawsuit pages, live letter URLs, etc.

## Target path mapping
| Live today | In this repo |
|---|---|
| `/` | `index.html` or keep letter as `index.html` and move trees to `tree.html` — TBD |
| `/ancestry/` | builder-squeezed tree; skip migrating this copy (GitHub already has the good tree) — leave it on NS |
| `/sutcliffe/.../` | `sutcliffe/.../index.html` (or `.html` with Pages pretty URLs) |
| `/riley/.../` | `riley/.../index.html` |
| `/bock/.../` | `bock/.../index.html` |

## Notes
- Website Builder cannot host a true standalone tree; that is why GitHub is home.
- Prefer clean exported HTML over another round of 1MB+ SingleFile dumps when practical.
- DNS for apex `pentimenti.org` will need GitHub Pages A/ALIAS records at Network Solutions; `www` can CNAME to `esutcliffe.github.io`.
