# The ecosystem you deploy into

Where your application would actually run, inside your actual firm.

> **Week 1 starts this file. Week 9 finishes it.**
> TC1 Step 10 asks eight questions. The full Week 9 checklist has around thirty,
> and the eight are a strict subset — so nothing here gets thrown away.

Describe patterns, not specifics. "On-prem OpenShift, images from an internal
registry, no public egress" is useful to everyone and identifies nobody. Never
put real hostnames, IPs, or architecture diagrams in this file.

---

## Week 1 — the first eight questions

<!-- Answered in TC1 Step 10. Bring these back from a real conversation. -->

**Who did you ask?** (role, not name)

Principal Software Engineer of my team

| # | Question | Answer |
| :---: | --- | --- |
| 1 | Where do internal apps run? (k8s, ECS, App Service, a VM someone maintains) | k8s |
| 2 | Which cloud? AWS, Azure, GCP, on-prem, several? | on-prem |
| 3 | Is there an internal container registry? | yes |
| 4 | How do users log in? (Okta, Entra ID, Ping, SAML, homegrown) | homegrown, SAML based LDAP or OAuth based LDAP |
| 5 | Can the app reach the internet? Egress proxy? Allowlist? | yes to all, but I will be using a local LLM model for now |
| 6 | Where do secrets come from? (Vault, Secrets Manager, Key Vault) | key vault, called snccredential |
| 7 | Who approves a deployment, and what review does it need? | There is a comprehensive process in place, where a team of architects will decide based on my proposal is sound enough, if I have architected all aspects of this solution correctly. They might suggest changes to the solution, or request additional information. But, I can deploy to the lab environment without any restrictions, that is where I will be starting my development. |
| 8 | Is there an approved internal LLM endpoint already? | no, for now, I am using a local LLM model. |

**What surprised you?**

I knew all the details, I have had these conversations with my team.

**What would you have to change about your app to deploy there?**

I do not know fully, but after testing things out in the lab environment, I will make changes as needed.
---

## Week 1 — what your machine told you
Date: 2026-10-16
host	why	status	signed by
pypi.org	Python packages	OK	GlobalSign nv-sa
files.pythonhosted.org	the actual wheel downloads	OK	GlobalSign nv-sa
api.openai.com	the model API	OK	Google Trust Services
cdn.jsdelivr.net	the CDN your app's frontend uses	OK	Sectigo Limited
huggingface.co	open weights and fine-tuning	OK	Amazon
registry-1.docker.io	container images	OK	Amazon
github.com	this repository	OK	Sectigo Limited


**Does this match what you were told in the table above?** Where it doesn't, that
gap is worth chasing — it usually means a proxy nobody documented.

---

## Week 9 — the full checklist

<!--
  TC9 extends this same file. Do not start a new one: the point is that the git
  history shows one continuous piece of work from Week 1 to Week 9.
-->

<!-- Week 9 -->
