import json, subprocess, os

os.chdir("/home/mark/youtube-auto")

# Create repo via curl with Auth header
f = open("/tmp/gh_token")
tok = f.read().strip()
f.close()
payload = '{"name":"youtube-auto","private":false,"description":"TubeForge - prophecy video automation"}'
auth_hdr = "" + "Authorization: Bearer " + tok + ""
cmd = ["curl", "-sL", "-X", "POST",
       "-H", auth_hdr,
       "-H", "Content-Type: application/json",
       "-d", payload,
       "https://api.github.com/user/repos"]
r = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
d = json.loads(r.stdout)
print("Repo:", d.get("full_name", d.get("message", "error")))

# Init git
subprocess.run(["git", "init"], capture_output=True)
subprocess.run(["git", "branch", "-m", "main"], capture_output=True)

# Check we have files
files = subprocess.run(["ls", "-la"], capture_output=True, text=True)
print("Files:", files.stdout[:200])

# Add and commit
subprocess.run(["git", "add", "-A"], capture_output=True)
r2 = subprocess.run(["git", "-c", "user.name=Ravi", "-c", "user.email=pnt01@foxmail.com",
                     "commit", "-m", "feat: TubeForge scaffold - prophecy video automation"],
                    capture_output=True, text=True)
print("Commit:", r2.stdout.strip()[:100] or r2.stderr.strip()[:100])

# Push
subprocess.run(["git", "remote", "add", "origin", 
                f"https://oauth2:{token}@github.com/shileibiz/youtube-auto.git"],
               capture_output=True)
r3 = subprocess.run(["git", "push", "-u", "origin", "main"],
                    capture_output=True, text=True, timeout=30)
print("Push:", r3.stdout.strip()[:200] or r3.stderr.strip()[:200])
