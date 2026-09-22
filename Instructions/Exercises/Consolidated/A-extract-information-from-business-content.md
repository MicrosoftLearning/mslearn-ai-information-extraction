---
lab:
    title: 'Extract information from business content'
    description: 'Extract structured information from the documents, images, audio, and video that flow through Fabrikam Logistics. Start in the Content Understanding portal, then go deeper with the Content Understanding SDK and with prebuilt and custom Document Intelligence models. A modular lab you can complete end to end or one task at a time.'
    level: 300
    concepts: 'Content Understanding, custom analyzers, Document Intelligence, prebuilt models, custom extraction models'
    duration: 40
    islab: true
    status: 'draft'
---

# Extract information from business content

**Difficulty** ▰▰▰▱▱ **L300**  (filled bars out of 5; **L100** beginner → **L500** expert)

Most of what a business knows is locked inside unstructured content: a PDF invoice, a photo of
a contact card, a slide deck, a voicemail, a recorded call. People can read all of it. Software
can't — until you extract it into fields. In this lab you'll build the extraction layer for
**Fabrikam Logistics**, using the two Azure services designed for exactly this job.

<style>
/* "Ask Rani" just-in-time concept blocks */
details.concept { margin:.6rem 0 1rem; }
details.concept > summary { display:inline-block; cursor:pointer; list-style:none;
  font-size:.85em; font-weight:600; color:#0b6a8f; background:#0b6a8f12;
  border:1px solid #0b6a8f33; border-radius:999px; padding:.2em .7em; }
details.concept > summary::-webkit-details-marker { display:none; }
details.concept > summary::before { content:"Ask Rani: "; font-weight:700; }
details.concept > summary:hover { background:#0b6a8f; color:#fff; border-color:#0b6a8f; }
details.concept[open] > summary { border-bottom-left-radius:0; border-bottom-right-radius:0; }
details.concept .concept-body { border:1px solid #0b6a8f33; border-top:none;
  border-radius:0 8px 8px 8px; padding:.6rem .9rem; background:#0b6a8f08; font-size:.95em; }
</style>

<details markdown="1" class="concept">
<summary>Content Understanding or Document Intelligence?</summary>
<div class="concept-body" markdown="1">

Both are part of **Foundry Tools**, and they solve different halves of the problem.

**Azure Content Understanding** is LLM-powered. You describe the fields you want in plain
language and it works across *any* modality — documents, images, audio, and video. Use it when
the content is varied or unstructured, or when you want a generated summary rather than a
literal value off the page.

**Azure Document Intelligence** is deterministic OCR-based extraction, tuned for documents. It
ships prebuilt models for common types (invoices, receipts, IDs), and you can train a **custom**
model on your own form layout. Use it when you need high-accuracy, repeatable, position-aware
extraction from documents that look the same every time.

Real solutions use both. This lab does too.

[Learn more →](https://learn.microsoft.com/azure/ai-services/content-understanding/overview)

</div>
</details>

**Your scenario:** you work at **Fabrikam Logistics**, a freight-forwarding company. Every day
the company receives supplier invoices in a dozen different layouts, contact cards collected by
reps at trade shows, quarterly review slides, voicemails from customers, and recordings of
operations calls. Nobody can keep up. Your job is to turn that flood of content into structured
fields that the rest of the business can actually use.

You'll start with the **Core** task, which gets you extracting from all four modalities as
quickly as possible. From there, a set of **Optional** tasks takes you from clicking in a portal
to writing the code, and from generative extraction to trained, deterministic models.

> **Note**: Some of the technologies used in this exercise are in preview or in active
> development. You may experience some unexpected behavior, warnings, or errors.

## What you'll learn

By completing the **Core** task of this exercise, you'll be able to:

- **Define a custom schema and build an analyzer** in Content Understanding that extracts named
  fields from documents, images, audio, and video — then test it against content it hasn't seen.

The **Optional** tasks let you additionally:

- **Create and call analyzers in code** with the Content Understanding Python SDK, so extraction
  runs inside your application instead of a portal.
- **Extract invoice data with a prebuilt model** using Azure Document Intelligence, with no
  schema and no training at all.
- **Train a custom extraction model** on your own form layout, and call it from Python when the
  prebuilt models don't fit your documents.

## How this lab is organized

This lab is **modular**. Each task is written to be completed **on its own, starting fresh** —
so you can pick a single task and do just that one. Every code task also shares one starter
folder, one virtual environment, and one `.env`, so if you'd rather work straight through, you
can.

1. **Start with [Getting started](A0-getting-started.md)** — create your Microsoft Foundry
   resource and project, connect Content Understanding, get the sample content and the starter
   code, and set up your `.env`. Every task begins here; if you're doing the whole lab in one
   sitting, you only need to do this once.
2. **Do any task.** Each task lists the setup it needs so you can start it independently. If
   you're moving straight from the previous task, a short *"Continuing from a previous task?"*
   note at the top lets you skip the repeated setup and keep going.

## Lab at a glance

Complete the **Core** task first (about **40 minutes**) — it ends with four working analyzers
covering documents, images, audio, and video. Then expand any **Optional** tasks that interest
you. The full lab, including all optional tasks, takes about **2 hours 15 minutes**.

| Section | Task | Difficulty | Time |
| --- | --- | --- | --- |
| **Core** | [Task 1 – Extract fields from multimodal content](A1-extract-fields-from-multimodal-content.md) | ▰▰▱▱▱ L200 | ~40 min |
| *Optional* | [Task 2 – Build an analyzer with the Python SDK](A2-build-an-analyzer-with-the-python-sdk.md) | ▰▰▰▱▱ L300 | ~30 min |
| *Optional* | [Task 3 – Extract invoice data with a prebuilt model](A3-extract-invoice-data-with-a-prebuilt-model.md) | ▰▰▰▱▱ L300 | ~25 min |
| *Optional* | [Task 4 – Train a custom extraction model](A4-train-a-custom-extraction-model.md) | ▰▰▰▱▱ L300 | ~40 min |

**Choosing your path** — pick the tasks that fit the time you have:

- **Core only (~40 min):** do Task 1 and stop. You'll have used Content Understanding across
  every modality.
- **Core + code (~1h 10m):** add **Task 2** to do the same thing from Python.
- **Documents in depth (~1h 45m):** do Task 1, then **Task 3** and **Task 4** to compare
  Content Understanding against Document Intelligence on the same kind of document.
- **Everything (~2h 15m):** all four tasks.

## Two services, one extraction layer

The tasks are ordered so each one changes exactly one thing:

- In **Task 1**, you use **Content Understanding** through the portal. You define what you want
  in a schema and the service figures out how to get it — across documents, images, audio, and
  video.
- In **Task 2**, you do the *same* Content Understanding work from **Python**. Same schema, same
  analyzer, now callable from an application.
- In **Task 3**, you switch to **Document Intelligence** and a **prebuilt** model. No schema at
  all: the model already knows what an invoice is.
- In **Task 4**, you stay in Document Intelligence but **train your own model** on labeled
  Fabrikam Logistics forms — the answer for documents no prebuilt model covers.

Seeing the generative approach first is what makes the deterministic, trained approach in
Tasks 3 and 4 meaningful.

## Summary

Across this lab you:

- Built **custom Content Understanding analyzers** for documents, images, audio, and video, and
  tested them on unseen content.
- (Optionally) created and called an analyzer with the **Content Understanding Python SDK**.
- (Optionally) extracted invoice fields with a **prebuilt Document Intelligence model**.
- (Optionally) **trained and tested a custom extraction model** on your own form layout.

Together these cover the full range of extraction: generative for anything, prebuilt for common
document types, and trained for documents that are uniquely yours.

Once your content is extracted, the natural next step is making it findable and answerable — see
[Make extracted information searchable](B-make-extracted-information-searchable.md).

## Clean up

If you're finished, delete the resources you created to avoid unnecessary Azure costs.

1. In the [Azure portal](https://portal.azure.com), navigate to the resource group that contains your Foundry and Document Intelligence resources.
1. On the toolbar, select **Delete resource group**, enter the resource group name, and confirm.
