# Secure Git Workflow

*Personal procedure for git operations that require GitHub authentication
(push, fetch with private repos, etc.) using a gpg-encrypted personal access
token. Generic to any repository.*

*Initial token creation and gpg encryption are documented in
`REPO_SETUP_PROCEDURE.md` (steps 5 and 6). This file covers ongoing
authenticated git operations only.*

---

## The threat model

GitHub no longer accepts account passwords for HTTPS git operations.
A personal access token is the required credential. Once obtained, the
token must be:

- Never written to disk in plaintext.
- Never typed into a shell command (where it would land in `.bash_history`).
- Never displayed on screen (where it could be screenshotted or seen by a
  shoulder-surfer).
- Stored encrypted, with the encrypted file isolated from the repository
  it authenticates against.

The procedure below satisfies all four constraints.

## Prerequisites

The encrypted token file `~/Desktop/<DDMMMYYYY>_devkey_<repo-name>.gpg`
must already exist. See `REPO_SETUP_PROCEDURE.md` steps 5 and 6 if it
does not.

## The decrypt-use-unset pattern

The pattern has three steps that execute as separate commands but in
immediate sequence:

```bash
TOKEN=$(gpg -d ~/Desktop/<DDMMMYYYY>_devkey_<repo-name>.gpg 2>/dev/null)
git push https://<username>:${TOKEN}@github.com/<username>/<repo-name>.git <branch>
unset TOKEN
```

Walking through what each line does:

**Line 1: decrypt to a shell variable.**
`gpg -d` decrypts the file. The output (the raw token) is captured into
the `TOKEN` environment variable by the `$(...)` command substitution.
GPG prompts for the passphrase you set during encryption. The `2>/dev/null`
suppresses GPG's status messages — the token itself is not affected.

The token now lives only in the `TOKEN` variable in the current shell's
memory. It is not on disk. It is not in shell history (because the
variable holds the value; the command line shown above contains no
plaintext token).

**Line 2: push using the variable.**
The `git push` URL embeds the username and the token. `${TOKEN}` expands
to the decrypted token value at command-execution time, after the line
is added to history. Shell history records the literal string
`${TOKEN}`, not its expanded value.

`<branch>` is typically `main`. Substitute the actual branch name.

**Line 3: unset the variable.**
`unset TOKEN` removes the variable from the shell's environment. After
this line, the token is gone from this shell. Any subsequent command
referencing `${TOKEN}` would get an empty string.

## Other authenticated operations

The same pattern applies to any git operation that authenticates against
GitHub. Replace `git push ... main` with the actual operation:

```bash
# Fetch from a private repo
TOKEN=$(gpg -d ~/Desktop/<DDMMMYYYY>_devkey_<repo-name>.gpg 2>/dev/null)
git fetch https://<username>:${TOKEN}@github.com/<username>/<repo-name>.git
unset TOKEN

# Pull from a private repo
TOKEN=$(gpg -d ~/Desktop/<DDMMMYYYY>_devkey_<repo-name>.gpg 2>/dev/null)
git pull https://<username>:${TOKEN}@github.com/<username>/<repo-name>.git <branch>
unset TOKEN
```

For public repos, fetch and pull do not require authentication;
this pattern is needed only for push to public repos and for any operation
on private repos.

## What this procedure prevents

- **Token in shell history.** The token never appears as a literal
  string on any command line. History contains `${TOKEN}` which is
  meaningless without the live shell variable.
- **Token in plaintext on disk.** Only the encrypted `.gpg` file is on
  disk. Decryption produces the token only in shell memory.
- **Token displayed on screen.** `gpg -d` writes to the captured command
  substitution, not to the terminal. The token is never rendered.
- **Token persisting after use.** `unset TOKEN` removes the variable
  immediately. Closing the terminal also destroys it.

## What this procedure does not protect against

Honest about limits:

- **A compromised machine.** If an attacker has root or your user account,
  they can read the token from memory while the variable is set, or
  install a keylogger to capture the gpg passphrase. This procedure is
  not a defense against full machine compromise.
- **Forgetting to unset.** If you decrypt the token and forget to run
  `unset TOKEN`, the variable persists in that shell until the shell
  closes. Other processes in the same shell session can read it.
- **Shoulder-surfing during passphrase entry.** GPG's passphrase prompt
  is visible. Choose passphrase entry times when you are not being
  observed.

## Token rotation

Personal access tokens expire (typically 90 days). When a token expires:

1. Generate a new token per `REPO_SETUP_PROCEDURE.md` step 5.
2. Encrypt the new token per step 6.
3. Verify the new `.gpg` file decrypts correctly by doing a benign
   authenticated operation (e.g., `git fetch`).
4. Delete the old `.gpg` file:
   ```bash
   rm ~/Desktop/<old-token-filename>.gpg
   ```

The naming convention `<DDMMMYYYY>_devkey_<repo-name>.gpg` makes the
current token obvious; the old one's date prefix flags it as stale.
