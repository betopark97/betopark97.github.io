# Personal Knowledge Management

PKM

Obsidian

Published

2026-06-27

I’ve tried a lot of different ways to manage my knowledge. I spent at least years trying to figure out what works best for me. Frameworks that other people have set, not me. However, I think that everyone has different ways to solve problems and different ways to study that suit them best.

I like simplicity and minimalism, but tend to get overwhelmed easily and just make a mess. After years of trying different tools and frameworks, finally I’ve settled down to making my own workflow and this feels way too comfortable - not to mention that I’m still migrating everything and I’ve come to realize what a huge mess I’ve made along the way.

The frameworks that I’ve tried until now were: MOC, PARA, Zettelkasten, respectively. These’s were either way too structured (PARA) or way too unstructured (Zettelkasten) or just tedious to manage (MOC), for me. Also, if moved from different platforms like Apple Notes -\> Notion -\> Obsidian -\> Notion -\> Obsidian. The reason I chose Obsidian is that the more I got into coding and the advancement of AI, it’s way easier to manage markdown files and I like the native Obsidian plugins, which solve most of the pain points I’ve had while using Notion (it’s the platform I’ve used the longest and customized the most).

> **NOTE:**
>
> Yes, the system I’ve built is also structured like PARA, but accustomed to my needs not something pre configured. While, Zettelkasten seems like a cool system, a big downside is that it’s hard to share with others meaning that it’s also hard to share with a future me.

That’s why I’ve chosen my own build to manage my knowledge. My personal workflow came to a more mature stage as I was making this personal website. And it is a mesh of MOC, PARA, and Zettelkasten along with some Obsidian native plugins like the BASE and CANVAS.

The architecture/structure consists of the following:

- `/archive`
  - This is the directory that is for anything that doesn’t seem to belong in any of the other directories.
- `/blog`
  - This is a directory for ideas that are shareable with the public.
- `/clippings`
  - This is for Obsidian clipping through a chrome extension to save articles that are worthy of being absorbed by my notes.
- `/inbox`
  - This is for sudden ideas that pop up and are mostly AI responses to structure my questions.
- `/notes`
  - This is the core of knowledge and place that absorbs ideas, clippings, to-dos, youtube content, etc. It is for having a structured, bite-sized documentation of things I study and apply.
- `/portfolio`
  - This is any documentation related to what goes into my career specs like the portfolio itself, CV and Resume.
- `/projects`
  - This brainstorming documentation for my projects, however it doesn’t store much because all project related documentation goes in the `docs/` directory inside the project, code-as-documentation, and in my to-do application.
- Other parts of my personal knowledge management are YouTube where most of my knowledge comes from other than blog articles and textbooks; and to manage my schedule, ToDoist.

This will sound something similar to David Allen’s “Getting Things Done” (GTD) Philosophy. Not that I created my own system knowingly, but making a reference to his philosophy does help to clarify what my system is doing. Also kind of a mix of C(apture), O(rganize), D(istill), E(xpress) by Tiago Forte.

1.  Capture: Collect anything and everything that has your attention into an inbox.
2.  Clarify: Determine if captured items are actionable. If not, trash them, incubate them, or file them as reference.
3.  Organize: Sort actionable tasks into logically categorized lists (e.g., next actions, projects, waiting-for).
4.  Reflect: Review and update your lists regularly to maintain clarity and trust in your system.
5.  Engage: Do the work based on your current context, time available, and energy levels.

Let’s go over how we will manage to do each step.

1.  Capture: most of my capture happens within YouTube, blog articles, textbooks, LLM chats.
    - YouTube -\> playlists (watch later, etc.)
    - Blog articles -\> clippings
    - Textbooks / LLM pinned chats -\> inbox

However, this is almost never linear as it seems because in the end, everything passes through an LLM filter for formatting, structuring, and fact checks.

2.  Clarify: from all the data that we have captured from different sources, these will differ in importance and maturity. If the data was a moments thing, which was captured but as an afterthought it’s not something I needed, doesn’t seem as important, or I’m not ready for it yet, it will be deleted/thrown away or it may just stay there as long as it needs and wait its turn to be digested to be part of my notes.

3.  Organize: this I believe is the most important part as it’s what and how knowledge gets absorbed and structured; something like a long term memory. The core would be the `/notes` directory which absorbs clippings, youtube video informations, completed todo tasks, textbook information, tool documentations, and more. However be aware that everything starts as a small idea and therefore everything starts as a single file and when many related ideas start to clutter the single file it becomes a folder. And this will change a lot over time. Think lots on how to structure your knowledge, as you give more thought the higher the probability of it staying with you longer. The key is malleability, and space to change than it being too rigid as that’s not really how our brain works, which is plastic. Something to note when managing data is also the importance of metadata. That’s why every single folder should have a index.md which is not exactly an index of the ideas inside the folder in the orthodox way but more like an abstract version of what goes in that folder along with the workflow if needed. This is to prevent documentation staleness like what I experienced with the MOC. All files must include some kind of YAML metadata at the top because file names should default to snake casing and no symbols. More of the file naming and project structuring conventions will be provided below.

4.  Reflect: this can happen on purpose, but mostly it should happen unconsciously in my opinion. The reflection should happen along with the engagement. If you have a well organized notes in your own words it should be documentation that you come back to frequently. Then you will realize if things need updates or deletion. And this would happen naturally.

5.  Engage: this is where we apply what we organized in the real world. The default key finding to search for a specific text in a file system in various tools is `Command + Shift + F` and that’s what works in Obsidian and that’s also what I’ve set on my personal website. This would be a `Command + Shift + K` in Notion, which I can free from my brain now.

In conclusion, I do know that this system might look a bit too overly complex, but like anything in life it’s only the beginning and it has become natural over time. That’s why this post is also something for myself, as a way to organize my thoughts kind of like a meta cognition. All in all, I would encourage anyone to make their own PKM as there are major benefits to managing a PKM. It reduces cognitive load to remember details - you just have to remember the location, which you put effort to structure so it’s easier to remember. Also it’s managing an external brain where knowledge compounds over time, adding value.

Back to top
