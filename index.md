---
title: Develop AI-powered information extraction solutions in Azure
permalink: index.html
layout: home
---

The following exercises are designed to provide you with a hands-on learning experience in which you'll explore common tasks that developers do when building AI-powered information extraction solutions in Microsoft Azure.

> **Note**: To complete the exercises, you'll need an Azure subscription in which you have sufficient permissions and quota to provision the necessary Azure resources and generative AI models. If you don't already have one, you can sign up for an [Azure account](https://azure.microsoft.com/free). There's a free trial option for new users that includes credits for the first 30 days.

## Exercises

<hr>

{% comment %}
  Only list pages that aren't drafts. A page opts out by setting `status: 'draft'`
  in its `lab:` front matter; a page with no `status` field is treated as
  publishable, so existing exercises are unaffected.
{% endcomment %}
{% assign labs = site.pages | where_exp:"page", "page.url contains '/Instructions/Exercises'" %}
{% for activity in labs  %}
{% if activity.lab.title and activity.lab.status != 'draft' %}

### [{{ activity.lab.title }}]({{ site.github.url }}{{ activity.url }})

{% if activity.lab.level %}**Level**: {{activity.lab.level}} \| {% endif %}{% if activity.lab.duration %}**Duration**: {{activity.lab.duration}} minutes{% endif %}

{% if activity.lab.description %}
*{{activity.lab.description}}*
{% endif %}
<hr>
{% endif %}
{% endfor %}
