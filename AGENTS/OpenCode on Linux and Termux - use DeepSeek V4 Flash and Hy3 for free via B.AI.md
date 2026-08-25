# How to install OpenCode on Linux and Termux and use "DeepSeek V4 Flash" and "Hy3" for free (limited time) through B.AI

OpenCode is an artificial intelligence programming agent that runs directly from
the terminal. Unlike a conventional chatbot, it can inspect a project's files,
modify code, run commands, and help us with software development tasks.

In this tutorial we will see how to:

- install OpenCode on Linux;
- install OpenCode on Android using Termux;
- get a B.AI API key;
- take advantage of the limited-time promotions of **DeepSeek V4 Flash** and **Hy3**;
- configure B.AI as an OpenCode provider;
- and query all the other artificial intelligence models available on B.AI in
  case you later want to use the paid service.

> **Important:** promotions can change. At the time of writing, B.AI shows
> **DeepSeek V4 Flash** and **Hy3** as *Limited-Time Free*. The B.AI documentation
> explicitly states that the DeepSeek V4 Flash promotion applies to Chat and to
> the API at **0 Credits**. Before starting a large job it is a good idea to check
> the **Usage** section of B.AI to verify the actual consumption of the account and
> confirm that the chosen promotion is still active.

---

# 1. Install OpenCode on Linux

OpenCode can be installed in several ways:

[https://opencode.ai/](https://opencode.ai/)

![](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEj00S4b-8gUky48d7y6SvOd-W8AjDm0DAohVaLuKCuLlfWWx0-SWueqr4-Ivk58hyphenhyphen1NpEjDGK14yp8oxPLajOKND5MukorWmWKhpbEXPGg6rvjByUy4LgXorLaZ_PGPOaBHFREA7eIhY-vnnrY7GuFWhdqPR9UaexB57pVBkjV0mF38XhT9eX_y_hWibwU/s1033/opencode.ai.png)

It has an official installer:

```bash
curl -fsSL https://opencode.ai/install | bash
```

This is the method I used.

On Debian- or Ubuntu-based distributions we can also install Node.js and npm with:

```bash
sudo apt update
sudo apt install nodejs npm
```

Then install OpenCode:

```bash
npm install -g opencode-ai
```

We can verify the installation with:

```bash
opencode --version
```

---

# 2. Install OpenCode on Android using Termux

The situation is different on Android.

Termux provides a Linux environment on top of Android, but Android uses Bionic
as the system C library and there are other differences compared with a regular
GNU/Linux distribution.

For this reason the community project **opencode-termux** exists, which builds
OpenCode specifically for Android/Termux on ARM64 (`aarch64`). The project
recompiles the necessary components so OpenCode can run natively in this
environment.

Project:

**guysoft/opencode-termux**

[https://github.com/guysoft/opencode-termux](https://github.com/guysoft/opencode-termux)

## Check the architecture

On Termux:

```bash
uname -m
```

To use these packages it must show:

```
aarch64
```

## Update Termux

```bash
pkg update && pkg upgrade
```

Install the required tools:

```bash
pkg install curl ripgrep
```

## Download OpenCode for Termux

It is recommended to check the project's releases first:

[https://github.com/guysoft/opencode-termux/releases](https://github.com/guysoft/opencode-termux/releases)

For example, a verified version is OpenCode 1.17.9 for Android/Termux aarch64,
published as release `v0.2.1`.

It can be downloaded like this:

```bash
cd ~
curl -LO https://github.com/guysoft/opencode-termux/releases/download/v0.2.1/opencode_1.17.9_aarch64.deb
```

Check the file:

```bash
ls -lh opencode_1.17.9_aarch64.deb
```

Then install it:

```bash
dpkg -i opencode_1.17.9_aarch64.deb
```

And make sure `ripgrep` is installed:

```bash
pkg install ripgrep
```

Finally:

```bash
opencode --version
```

To launch it:

```bash
opencode
```

The `opencode-termux` project also offers other installation formats, including
a standalone executable and Pacman packages.

> **Note:** OpenCode evolves quickly. Before installing it on Termux it is a good
> idea to check the Releases page and use the newest compatible version, instead
> of assuming the version number shown in this tutorial is still the latest.

---

# 3. What is B.AI?

B.AI provides access through a single API to different artificial intelligence
models.

A particularly interesting advantage is that its API uses an interface
compatible with the OpenAI format, which allows connecting it to applications
that support custom providers, including OpenCode.

The base URL we will use is:

```
https://api.b.ai/v1
```

---

# 4. Create a B.AI API key

First we must create an account on B.AI.

```
https://chat.b.ai/
```

After creating it we can see the available promotions, for example:

"DeepSeek V4 Flash: Limited-Time Free"

"Hy3: Limited-Time Free"

![](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjy8XOMBijyuiCvupyySXk-XAj3dqm173xqV5Kp-HitTlNRqILBnUMKC0ZBb01b8R2hbH5I13Qgag89adsVvc-ODRbCFB06_71rB0BA5YsMN3-Gff4YOAi-0iyJoYud0BitoGo12jeEwNDFgqrzGP0-TpYLVEqJ86apNI__ie5P-CtjSAyeIttAzV1GcMM/s1116/chat.b.ai_chat.png)

Then we go to:

```
https://chat.b.ai/key
```

![](https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEglgpgH8WMLxpRx0xYPLh3Wob4E0LRFaddoZFl-X6ouhF-EtM1uSVU3EuQFX8pmuY48TZ-x9YsJBptLiuKszp2hlBb7z1xacbDIPLrKTRDgQ1RFbIAoW874N7RlzRVlOK-LSvT-MKjeLMbAH1CaL4EzH0CT3JU8vDFHj051u_hqIercpBxlz-VID1d-jck/s1184/chat.b.ai_key.png)

From there we create a new API key.

The key will look something like:

```
sk-xxxxxxxxxxxxxxxxxxxxxxxx
```

We must copy it and keep it in a safe place.

## ⚠️ Do not publish the API key

An API key works like a password.

We must not:

- publish it on GitHub;
- include it in screenshots;
- write it in tutorials;
- send it to other people;
- or store it directly inside our programs' code.

In the examples of this tutorial we will use:

```
TU_API_KEY
```

The user must replace it locally with their real key.

---

# 5. DeepSeek V4 Flash for free through B.AI

This is the most interesting part of the tutorial.

B.AI started a promotion on **August 17, 2026** for:

```
DeepSeek-V4-Flash
```

During this promotion, using it through B.AI Chat and through the API is billed
at:

```
0 Credits
```

According to B.AI, during the promotion neither input tokens, output tokens,
cache writes nor cache reads are charged.

This is especially interesting for programs like OpenCode, because a programming
agent can make many requests while it:

- inspects files;
- studies a project;
- modifies code;
- runs commands;
- analyzes errors;
- and keeps working on the results.

DeepSeek V4 Flash is also oriented to programming tasks and agent usage. It has
support for tool/function calling and a context window of up to **1 million
tokens**.

The promotion is temporary. B.AI states that when it ends, the model will return
to its normal price.

---

## 5.1. DeepSeek V4 Flash vs Hy3: which one to use?

B.AI currently shows two models marked as **Limited-Time Free**:

- **DeepSeek V4 Flash**
- **Hy3**

Both are interesting for using OpenCode as a programming agent, but they have
different characteristics.

| Feature | DeepSeek V4 Flash | Hy3 |
|---|---|---|
| Programming | Yes, very code-oriented | Yes, oriented to programming agents |
| Agent usage | Yes | Yes |
| Tool / Function Calling | Yes | Yes |
| Maximum context | **1,000,000 tokens** | **256,000 tokens** |
| Maximum published input | — | **192,000 tokens** |
| Maximum output | **384,000 tokens** | **128,000 tokens** |
| Multimodal | No, text only | No, text only |
| Work with repositories | Yes | Yes |
| Multi-step tasks | Yes | Yes |
| Model ID on B.AI | `deepseek-v4-flash` | `hy3` |

### Which one is best to use in OpenCode?

For large projects, **DeepSeek V4 Flash has a very important advantage: its
1 million token context window**. This can be useful when OpenCode needs to keep
a large amount of code, files, and results in context while working.

**Hy3**, on the other hand, is oriented to software-engineering agent work and
is suitable for programming tasks that require planning, repeated use of tools,
code modification, debugging, and multi-step work.

A practical strategy is to have **both configured** and switch between them from
OpenCode using:

```text
/models
```

This way we can try them with our own projects and decide which one gets better
results in each situation.

## 5.2. Check the consumption on B.AI

Although we may be using a model that appears under a free promotion, it is
recommended to periodically check the consumption of our account.

Go to B.AI and, in the side menu, select:

```text
Usage
```

From there we can review the usage made by our account.

This is especially recommended because promotions are temporary and can change.
Also, the fact that a model appears when querying `/v1/models` means it is
available in the API catalog, **not necessarily that its usage is free**.

For this reason, before starting a large job with OpenCode it is a good idea to
verify that the chosen model is still included in the promotion and review the
**Usage** section afterwards.

# 6. Connect B.AI with OpenCode

We start OpenCode:

```bash
opencode
```

Inside OpenCode we type:

```
/connect
```

We look for the option to add another provider, usually:

```
Other
```

When OpenCode asks for a provider identifier we type:

```
bai
```

When it asks for the API key, we paste the key we obtained earlier.

OpenCode stores its credentials separately, so **it is not necessary to write
our API key directly inside `opencode.json`**.

---

# 7. Configure DeepSeek V4 Flash and Hy3

Now we must tell OpenCode where the B.AI API is and which model we want to use.

Inside the project directory we must create:

```bash
nano opencode.json
```

Paste the following so OpenCode recognizes the **DeepSeek V4 Flash (B.AI)** and
**Hy3 (B.AI)** models:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "provider": {
    "bai": {
      "npm": "@ai-sdk/openai-compatible",
      "name": "B.AI",
      "options": {
        "baseURL": "https://api.b.ai/v1"
      },
      "models": {
        "deepseek-v4-flash": {
          "name": "DeepSeek V4 Flash (B.AI)"
        },
        "hy3": {
          "name": "Hy3 (B.AI)"
        }
      }
    }
  }
}
```

Save in Nano with:

```
Ctrl + O
Enter
Ctrl + X
```

There is a very important detail.

The identifier:

```
bai
```

must match the identifier used earlier when running `/connect`.

---

# 8. Start OpenCode and select DeepSeek V4 Flash or Hy3

Enter the directory of our project:

```bash
cd MiProyecto
```

Run:

```bash
opencode
```

Inside OpenCode we can open the model selector with:

```
/models
```

There we look for:

```
B.AI
```

It should show:

```
DeepSeek V4 Flash (B.AI)
Hy3 (B.AI)
```

We select the model we want to use.

From that moment we can ask it to do tasks such as:

```
Analyze this project and explain its architecture before making any changes.
```

Or, for example:

```
Continue with the port of this program to PyQt6. First review the current state
of the project and the changes already made before modifying files.
```

OpenCode will be able to use DeepSeek V4 Flash or Hy3 as an agent to inspect,
modify, and work on our project. We can switch models later with `/models`.

---

# 9. Check directly that the API works

We can also check the API from the terminal without using OpenCode.

We use:

```bash
curl -X POST "https://api.b.ai/v1/chat/completions" \
  -H "Authorization: Bearer TU_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "deepseek-v4-flash",
    "messages": [
      {
        "role": "user",
        "content": "Hello World"
      }
    ],
    "stream": false,
    "max_tokens": 1000
  }'
```

We must replace:

```
`TU_API_KEY`
```

with our real API key.

If we receive a response generated by the model, the API is working correctly.

---

# 10. What about GPT, Claude, Gemini and the other models?

B.AI does not only offer DeepSeek and Hy3.

Its API provides access to many models from different families, including:

- GPT;
- Claude;
- Gemini;
- DeepSeek;
- GLM;
- Kimi;
- Qwen;
- MiniMax;
- MiMo.

But we have to be careful about one thing:

> **The fact that a model appears as available in the API does not mean it is
> free.**

Some models require having a balance or making a deposit.

For example, if we try to use a premium model without meeting the account
requirements, B.AI may respond with a message similar to:

```
Access restricted. Deposit required to unlock premium models.
```

In this tutorial we have configured the two models that B.AI currently shows
with the **Limited-Time Free** label:

```text
deepseek-v4-flash
hy3
```

However, we must remember that these promotions are temporary. Before using any
of these models we should check on the B.AI page whether the promotion is still
active and review the **Usage** section to verify the Credits consumption.

The other models that appear when querying the API should not be considered free
just because they appear in the list. Some have a price per token and others may
require a balance or a prior deposit to be used.

---

# 11. See all the artificial intelligences available on B.AI

If we later want to buy Credits or simply want to know the models B.AI has
available through our API, we can query them directly.

First we install `jq`.

## On Debian, Ubuntu and derivatives

```bash
sudo apt install jq
```

## On Termux

```bash
pkg install jq
```

Then run:

```bash
curl -s "https://api.b.ai/v1/models" \
  -H "Authorization: Bearer TU_API_KEY" |
jq -r '.data[].id'
```

Replace `TU_API_KEY` with our key.

We will get a list similar to:

```
minimax-m3
minimax-m2.7
glm-5.1
glm-5.2
gpt-5.6-sol
gpt-5.6-terra
gpt-5.6-luna
gpt-5.5
gpt-5.4
gpt-5.2
claude-opus-5
claude-sonnet-5
claude-sonnet-4.6
gemini-3.1-pro
gemini-3.6-flash
kimi-k2.6
glm-5.3
kimi-k3
qwen3.8-max
deepseek-v4-flash
deepseek-v4-flash-vision-exp
deepseek-v4-pro
qwen3.8-27b
mimo-v2.5
mimo-v2.5-pro
```

The list may change over time, so **it is preferable to use the previous command
instead of relying on a list written in a tutorial**.

---

# 12. Query the models without `jq`

If we don't want to install `jq`, we can also query the JSON response directly:

```bash
curl -s "https://api.b.ai/v1/models" \
  -H "Authorization: Bearer TU_API_KEY"
```

The information will be less convenient to read, but it will show the models the
API has available.

---

# 13. Add other models to OpenCode later

Suppose that in the future we decide to use the paid service and want to add
other models.

We can extend the `"models"` section of our `opencode.json`.

For example, from what the previous command returned I made a list that I want
to try:

deepseek-v4-flash
glm-5.3
qwen3.8-max
claude-sonnet-5
gpt-5.6-sol

With this list we can create a configuration like the following. We can also ask
an AI to help us prepare the configuration block:

```json
"models": {
  "deepseek-v4-flash": {
    "name": "DeepSeek V4 Flash (B.AI)"
  },
  "glm-5.3": {
    "name": "GLM 5.3 (B.AI)"
  },
  "qwen3.8-max": {
    "name": "Qwen 3.8 Max (B.AI)"
  },
  "claude-sonnet-5": {
    "name": "Claude Sonnet 5 (B.AI)"
  },
  "gpt-5.6-sol": {
    "name": "GPT-5.6 Sol (B.AI)"
  }
}
```

Before using paid models we should always check B.AI's current prices, because
each model can have different prices for input, output and cache tokens.

---

# 14. Why are DeepSeek V4 Flash and Hy3 interesting for OpenCode?

For a programming agent it is not only important that the model can generate
code.

OpenCode needs the model to take part in a loop like this:

```
User
   ↓
OpenCode
   ↓
B.AI
   ↓
DeepSeek V4 Flash / Hy3
   ↓
Analyzes the project
   ↓
Requests to run a tool
   ↓
OpenCode runs the command
   ↓
Returns the result to the model
   ↓
The model analyzes the result
   ↓
Modifies files, runs tests
or performs another action
```

DeepSeek V4 Flash and Hy3 support *tool calling* and are prepared for
programming and agent work. DeepSeek V4 Flash also stands out for its context
window of up to 1 million tokens.

This allows using it not only for simple questions, but also to work as an agent
on software projects.

---

# 15. Summary

The configuration we have made looks like this:

```
Linux or Android/Termux
        │
        ▼
     OpenCode
        │
        ▼
@ai-sdk/openai-compatible
        │
        ▼
 https://api.b.ai/v1
        │
        ▼
       B.AI
      ╱    ╲
     ▼      ▼
DeepSeek   Hy3
V4 Flash
```

This way we can use OpenCode from Linux or even from an Android phone using
Termux and connect it with DeepSeek V4 Flash or Hy3 using the B.AI API. From
`/models` we can switch between the models we have configured.

The documented DeepSeek V4 Flash promotion started on **August 17, 2026** and
B.AI states it is temporary. B.AI also shows Hy3 as **Limited-Time Free** in its
interface. Therefore it is a good idea to check the status of both promotions
and the **Usage** section before following this tutorial in the future.

While the promotion remains active, it is a particularly interesting opportunity
for those who develop free software, maintain large projects, or want to
experiment with programming agents without quickly consuming credits from
commercial services.

## Official links

**OpenCode:**

```
https://opencode.ai/
```

**OpenCode documentation:**

```
https://opencode.ai/docs/
```

**B.AI:**

```
https://chat.b.ai/
```

**Create/manage the B.AI API key:**

```
https://chat.b.ai/key
```

**B.AI API documentation:**

```
https://docs.b.ai/llmservice/api/
```

**DeepSeek V4 Flash info on B.AI:**

```
https://docs.b.ai/llmservice/models/deepseek-v4-flash/
```

**Hy3 info on B.AI:**

```
https://docs.b.ai/llmservice/models/hy3/
```

**B.AI promotions and pricing notices:**

```
https://docs.b.ai/llmservice/promotions-and-pricing-notices/
```

---

# 16. Real case: the port of TBO to Python/PyQt6

This tutorial was written from a real project that allows comparing the
practical experience with the two promoted models.

The project is **TBO**, a comic editor originally written in **C and GTK 3**
(unmaintained since 2013). It was fully reimplemented in **Python/PyQt6**,
keeping compatibility with the historical `.tbo` format, and adding an asset
library, undo/redo, PNG/PDF/SVG export, translations (English/Spanish) and
Debian packaging.

Port repository:

```
https://github.com/wachin/TBO
```

The experience with each model was the following:

### Hy3

The `hy3` model was configured and used in OpenCode to start the work.
During this test **only 3 commits could be made and pushed**; from that point on
the agent returned a message indicating that it could no longer continue (that
was as far as the allowance went). With Hy3 the port could not progress.

### DeepSeek V4 Flash

With the `deepseek-v4-flash` model the **full port of TBO to PyQt6 was
completed**, including:

- the reimplementation of the document model and the `.tbo` reader/writer;
- the interactive canvas and undo/redo commands;
- the asset library (Doodles, Character, Accessories, Bubbles);
- text editing and icons;
- PNG, PDF and SVG export;
- Qt Linguist translations;
- the `.deb` packaging and CI workflows;
- and the final repository reorganization (legacy code under `legacy/`).

This tutorial and the files in this repository were generated with **DeepSeek
V4 Flash** through B.AI, in OpenCode.

In short, in this real case **Hy3 was limited to a few commits**, while
**DeepSeek V4 Flash allowed finishing the whole project**. Therefore, for long or
multi-session jobs, DeepSeek V4 Flash proved to be the more reliable option of
the two promotions active at the time of writing.

> Remember: promotions are temporary. Before starting a large job it is a good
> idea to check on B.AI that the chosen model is still included in the promotion
> and review the **Usage** section while working.

---

God bless you
