# Repository Setup Procedure

*Personal procedure for creating a new GitHub-backed repository from scratch.
Covers local directory creation, git initialization, GitHub repo creation,
fine-grained token setup, and the first push. Generic to any new project.*

*Secure token handling is documented separately in `SECURE_GIT_WORKFLOW.md`.
This file references that workflow for the push step but does not duplicate it.*

---

## 1. Create the local project directory

From the projects parent directory:

```bash
cd ~/Desktop/projects
mkdir <repo-name>
cd <repo-name>
```

The local directory name should match the GitHub repo name exactly.
Mismatch causes friction every time you reference the path.

## 2. Initialize git locally

```bash
git init
git branch -m main
git status
```

`git init` creates an empty `.git/` directory. `git branch -m main` renames
the default `master` branch to `main` immediately, before any commits — this
avoids a rename later. `git status` confirms you're on `main` with no commits.

## 3. Create the GitHub repository

Go to `github.com/new` and configure:

- **Owner** — your GitHub account.
- **Repository name** — must match the local directory name.
- **Description** — one or two sentences. A reviewer reads this in the repo
  list view before clicking in.
- **Visibility** — Public for portfolio artifacts; Private for proprietary work.
- **Add README** — leave **Off**. The local README will be written separately
  and pushed; do not let GitHub initialize one.
- **Add .gitignore** — select **Python** (or whichever language fits) from the
  dropdown. Saves writing one manually.
- **Add license** — select **MIT License** for permissive open-source.
  Choose deliberately for proprietary work.

Click **Create repository**.

## 4. Connect the local directory to GitHub

GitHub initialized the repo with `.gitignore` and `LICENSE` files. The local
directory must pull those down before any local commits can be pushed.

```bash
git remote add origin https://github.com/<username>/<repo-name>.git
git pull origin main
```

After this, `ls -alh` should show `.gitignore`, `LICENSE`, and `.git/` in the
local directory.

## 5. Create a fine-grained personal access token

GitHub no longer accepts account passwords for HTTPS git operations.
A fine-grained personal access token is the required credential.

Go to `github.com/settings/personal-access-tokens/new` and configure:

- **Token name** — `<DDMMMYYYY>_devkey_<repo-name>` (e.g.
  `30MAY2026_devkey_inference-workbench`). Consistent naming across all
  tokens makes the token list scannable.
- **Resource owner** — your account.
- **Expiration** — 90 days is the standard interval. Longer is convenient
  but increases blast radius if a token leaks.
- **Repository access** — **Only select repositories** → select the new repo.
  Never use "All repositories" — a leaked token with all-repo access can
  modify every repo you own.
- **Permissions** — under Repositories:
  - **Contents** → Read and write (required for push)
  - **Metadata** → Read-only (auto-required, cannot be disabled)

Click **Generate token**. Copy the token to clipboard.
**Do not paste the token anywhere except the gpg encryption command in step 6.**

## 6. Encrypt the token with gpg

The token must never be written to disk in plaintext, and must never be typed
into a shell command (where it would land in `.bash_history`).

The clean method:

```bash
gpg -c -o ~/Desktop/<DDMMMYYYY>_devkey_<repo-name>.gpg
```

The terminal will wait for input. **Paste the token, then press Ctrl-D.**
Do not press Enter — pressing Enter inserts a newline character into the
encrypted content, which will break authentication when the token is later
decrypted.

GPG will prompt for a passphrase twice. Choose a strong passphrase and
store it in a password manager. The passphrase protects the encrypted file
if it is ever copied off-machine.

Verify the file exists:

```bash
ls -alh ~/Desktop/<DDMMMYYYY>_devkey_<repo-name>.gpg
```

The token is now stored encrypted, with no plaintext copy anywhere on disk.

## 7. Create the initial repository structure

What gets committed first depends on the project. Common patterns:

- A documentation-first project — write `README.md` and `ARCHITECTURE.md` first.
- A code-first project — scaffold module directories with placeholder
  `__init__.py` and `README.md` files inside each, so empty directories
  are tracked.
- Any project — `NEXT_TASKS.md` to seed the working task list.

For a module-scaffold pattern, the bash idiom is:

```bash
mkdir -p module_a module_b module_c
for module in module_a module_b module_c; do
  touch "$module/__init__.py"
  echo "# $module" > "$module/README.md"
done
```

`mkdir -p` creates multiple directories at once. The loop populates each
with the two files git needs to track them.

## 8. Stage and commit

```bash
git add .
git status
git commit -m "<short summary>

<longer rationale paragraph explaining why, not just what>"
```

Multi-line commit messages with a rationale paragraph are worth the extra
seconds. The summary line is what shows in `git log --oneline`; the body
is what a reviewer (or future-you) reads when investigating why a change
was made.

## 9. Push the first commit

See `SECURE_GIT_WORKFLOW.md` for the secure decrypt-and-push procedure.
The short form:

```bash
TOKEN=$(gpg -d ~/Desktop/<DDMMMYYYY>_devkey_<repo-name>.gpg 2>/dev/null)
git push https://<username>:${TOKEN}@github.com/<username>/<repo-name>.git main
unset TOKEN
```

GPG prompts for the passphrase. The token is decrypted into a shell
variable, used immediately, and unset. It never appears on screen or in
shell history.

## 10. Verify on GitHub

Refresh the GitHub repo page. The first commit should appear with the
expected files. The repo is now ready for normal development.

---

## Notes

- **Token lifetime is 90 days.** When a token expires, generate a new one
  following step 5, encrypt it following step 6, and delete the old `.gpg`
  file. The naming convention with the date prefix makes the latest token
  obvious at a glance.
- **One token per repo, not one token for everything.** A leaked
  single-repo token has bounded blast radius. A leaked all-repo token
  does not.
- **The `.gpg` file lives outside the repository.** Never commit it,
  never reference it from inside the repo directory.
