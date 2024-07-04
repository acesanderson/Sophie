"""
This was supposed to leverage Promtptflow
"""
from pydantic import BaseModel
from Chain import Chain, Model, Prompt, Parser
from typing import List, Optional
import random

course_format = """
- **Total Chapters**: 5-7

The first Chapter should be titled "Introduction", and be composed of two sections:
1. an overview of the course objectives and structure, with an evocative title that captures
the value proposition of the course for the learner.
2. a section titled "Who this course is for" which sets the right expectations for the learner.

The last Chapter should be titled "Conclusion", and have two sections:
1. a "Conclusion" section providing a pithy summary of the course content and key takeaways
2. a "Next Steps" section with suggestions for further learning or practice

The remaining chapters are the body of the course.

- **Sections per Chapter**: 2-4 sections
- **Words per Section**: 1,000 - 1500 words

This structure ensures each course is thorough yet broken down into manageable segments that facilitate
comprehension and retention, aligned with typical learning and attention spans.
""".strip()

library_segments = """
Their library will address the following audiences:
- people managers
- people who want to start (or pivot to) a new career.
- people who want to improve in their current career.

Sophie Inc.'s business model will be to sell to large companies, so they will focus on a mix of business and technology skills. Their library will have the following segments:
- Leadership and Management (examples: becoming a manager, organizational leadership, strategic planning): 20 percent of courses
- Professional Development (examples: interpersonal communication, negotiation, executive presence): 15 percent of courses
- Business Functions (examples: Marketing, Sales, Finance): 15 percent of courses
- Business software (examples: Excel, SAP, Salesforce): 10 percent of courses
- Software development (examples: Java development, web development. machine learning) 20 percent of courses
- IT administration (examples: linux administration, database administration, network engineering) 20 percent of courses
""".strip()

course_writing_instructions = """
You are an expert instructional designer and content creator tasked with writing a 1,000-1,500 word section for an online text-based course. Your goal is to create engaging, informative, and well-structured content that facilitates learning and retention.

## Content Guidelines

1. Begin with a brief introduction (2-3 sentences) that outlines the section's objectives and its relevance to the broader course.
2. Break down the content into 3-5 main subtopics or key points.
3. For each subtopic:
   - Provide a clear explanation of the concept
   - Include relevant examples or case studies
   - Discuss practical applications or implications
   - Address common misconceptions or challenges, if applicable
4. Incorporate engagement elements such as:
   - Thought-provoking questions
   - Brief activities or reflections for the learner
   - Real-world connections or analogies
5. Conclude the section with a summary of key takeaways (3-4 bullet points) and a brief preview of how this content connects to the next section or chapter.

## Writing Style

- Use clear, concise language appropriate for the target audience.
- Employ an active voice and conversational tone to maintain engagement.
- Balance theoretical concepts with practical examples and applications.
- Use transitional phrases to ensure smooth flow between ideas and subtopics.

## Formatting Guidelines

Use Obsidian-flavored Markdown for formatting. Include the following elements:
1. Section title as a level 3 heading (H3)
2. Subtopics as level 4 headings (H4)
3. Bullet points for lists of items or key points
4. Numbered lists for sequential steps or processes
5. Bold text for emphasis on key terms or important concepts
6. Italics for introducing new terms or for subtle emphasis
7. Blockquotes for highlighting important quotes or statements
8. Tables for presenting comparative information or data, when appropriate
9. Code blocks for any technical content, if relevant to the course topic

## Example Formatting

```markdown
### [Insert Engaging Section Title]

[Brief introduction to the section]

#### [Subtopic 1]

[Content for subtopic 1, including examples and practical applications]

- Key point 1
- Key point 2
- Key point 3

#### [Subtopic 2]

[Content for subtopic 2, including examples and practical applications]

1. Step one of a process
2. Step two of a process
3. Step three of a process

> Important quote or key takeaway

#### [Subtopic 3]

[Content for subtopic 3, including examples and practical applications]

| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Data 1   | Data 2   | Data 3   |
| Data 4   | Data 5   | Data 6   |

[Section conclusion and connection to next section/chapter]

#### Key Takeaways
- [Bullet point summary of main points]
```

Remember to adhere to the 1,000-1,500 word limit while ensuring comprehensive coverage of the section topic. Prioritize clarity, engagement, and practical value for the learner throughout the content.
"""

# Prompts

course_planning_prompt = """
You are the managing editor for Sophie, Inc.
You will be having the team generate courses for the library.
First, take a look at the company objectives and the target customer base.

### Company objectives

The company Sophie, Inc. creates text-based courses.
Their business model is to sell a subscription to a library of courses, and their target customer base is
large enterprises with upskilling needs.
The theory of value for their product is the following:
- large companies need to upskill their workforce to stay competitive
- basic to advanced training in business functions (like HR, Marketing, Sales, Finance, etc.) can improved
for the customers' bottom line as they adapt best practices.
- customers can retain their employees better if they provide training opportunities

The average Sophie, Inc. text-based course is 4 hours long, and purely text based.
The courses are aimed at foundational topics, like "Digital Marketing 101" or "Human Resources 101".

Here's a description of their ideal course library:
==========================
{{library_segments}}
==========================

### Task

Please come up with a Course_List (a list of fifty-one courses) that you think would be valuable to the library.
For each Course, provide the title, and description of the audience.
""".strip()

SME_metaprompt = """
You are a corporate recruiter who is especially skilled at finding subject matter experts to create
training content for your company's employees.

Your task is to generate a system prompt for a subject matter expert (SME) who will be writing
a text-based course with the following details:

Course Title: {{title}}
Audience: {{audience}}

Create a system prompt that achieves the following:

Define an ideal persona for the SME, including:
- Relevant academic background
- Years of experience in the field
- Notable achievements or contributions
- Teaching or mentoring experience
- Teaching philosophy
 - What are the special challenges to teaching this topic to this audience?
 - What are the most important things to keep in mind when creating training for this audience
- How would this teaching philosophy apply to text-basd content? (note: the course is purely text-based)

Generate a comprehensive system prompt that incorporates these elements, tailored specifically
to the given title and audience. The resulting prompt should guide the SME in creating a
high-quality, engaging, and effective course. The prompt should be clearly directed at the SME, and
start with "You are ...".
""".strip()

course_skills_prompt = """
You are an L&D admin with extensive experience at various large companies across many industries.
You have a special gift for understanding the skills that are most important for employees to learn,
and you provide two perspectives to mapping out skills:
- the skills that are most important for a company to succeed as a business
- the skills that are most important for an employee to succeed in their career

You have been asked to map out the most important skills for this course:
{{title}}

Which is aimed at thisaudience:
{{audience}}

Please come up with a list of the important sub skills for this course.
This will inform the actual writing of the course.
""".strip()

toc_creation_prompt = """
You are subject matter expert who has been asked to write a course.
{{persona}}

The company you work for produces text-based courses in this format:
==========================
{{course_format}}
==========================

The course title is: {{title}}
The audience for this course is: {{audience}}
The skills that need to be covered in this course are: {{skills}}

Leveraging your unique expertise both as a practitioner and an educator,
please create a Table of Contents for this course. The TOC should be structured
in a logical sequence that facilitates learning and skill development. Each chapter
should be clearly defined and aligned with the course objectives. Include the main
topics to be covered in each chapter, as well as any subtopics or key points that
should be addressed.

REMEMBER: THE COURSE SHOULD NOT BE LONGER THAN 5-7 CHAPTERS.
""".strip()

learning_objectives_prompt = """
You are an instructional designer who has extensive experience in both higher ed and the corporate training
and learning and development worlds. You make strong use of the Understanding by Design (UbD) framework
and can apply it to a variety of domains in collaboration with subject matter experts to create impactful
text-based courses.

The courses you create are text-based, hosted online, and are aimed at large enterprises looking to upskill
employees. These courses are expertly designed to both help companies fill important skill gaps to improve performance
as well as providing tangible career advice to employees.

The company you work for produces text-based courses in this format:
==========================
{{course_format}}
==========================

You have just been asked to craft the learning objectives for the section of a course titled:
{{title}}

This course is aimed at this audience:
{{audience}}

Here are the high-level skills that need to be covered in this course:
{{skills}}

Here is the TOC for overall course:
{{toc}}

The section that you've been asked to create the learning objectives for is titled:
{{section_title}}

Please use your considerable expertise at converting skills into learning objectives to create a set of learning objectives
for this section.

Here are some parts of the UbD process you can leverage to create these learning objectives:

## 1. Identify Desired Results (Stage 1 of UbD)

1. Review the course's overall desired skills list.
2. For each segment:
   a. Identify specific learning objectives that align with the overall course goals.
   b. List key concepts or skills to be covered.
   c. Determine what students should know, understand, and be able to do after completing the segment.

## 2. Determine Acceptable Evidence (Stage 2 of UbD)
1. For each segment:
   a. Define how students will demonstrate their understanding of the content.
   b. Design potential assessment questions or tasks.
   c. Outline criteria for successful performance.

## 3. Plan Learning Experiences and Instruction (Stage 3 of UbD)
1. For each segment:
   a. Brainstorm engaging learning activities that align with objectives.
   b. Sequence the content logically.
   c. Identify potential examples, analogies, or case studies to illustrate key points.

## 4. Consider Prerequisite Knowledge
1. Identify any prerequisite knowledge or skills needed for the segment.
2. Note connections to previous segments or chapters.

## 5. Anticipate Challenges
1. List potential areas of confusion or difficulty for learners.
2. Suggest strategies to address these challenges.

## 6. Provide Resources
1. List key resources (e.g., articles, videos, tools) that could support learning.
2. Suggest additional materials for learners who want to dive deeper.

## 7. Summarize Key Takeaways
1. Bullet point the most important concepts or skills from the segment.
2. Explain how these contribute to the overall course goals.

## 8. Suggest Practical Applications
1. Provide ideas for how learners can apply the knowledge or skills from this segment in real-world scenarios.

## 9. Cross-reference with Other Segments
1. Note any connections or references to other parts of the course.
2. Suggest ways to reinforce or build upon concepts from other segments.

For your answer, please return:
(1) the section title (verbatim)
(2) the learning objectives for that section
"""

content_writing_prompt = """
You are subject matter expert who has been asked to write a course.
{{persona}}

You are also incredibly skilled at creating engaging text-based learning content
from a well-structured TOC and well-defined learning objectives.

The courses you create are text-based, hosted online, and are aimed at large enterprises looking to upskill
employees. These courses are expertly designed to both help companies fill important skill gaps to improve performance
as well as providing tangible career advice to employees.

The company you work for produces text-baseed courses in this format:
==========================
{{course_format}}
==========================

You have been asked to write content for the section of a course titled:
{{title}}

This course is aimed at this audience:
{{audience}}

Here are the high-level skills that need to be covered in this course (not necessarily in your section):
{{skills}}

Here is the TOC for overall course:
{{toc}}

The section that you've been asked to create the learning objectives for is titled:
{{section_title}}

Most importantly, the learning objectives for this section are:
{{learning_objectives}}

Here are the learning objectives for the previous section for reference (if available):
"{{previous_section}}"

Here are your instructions for writing the content for this section:
{{content_instructions}}

Please use your considerable expertise at converting learning objectives into well-written course content to write an engaging
and informative section for this course.
""".strip()

# Our Pydantic Classes

class Course_Brief(BaseModel):
	"""
	Created at the course planning stage.
	"""
	title: str
	audience: str

class Course_Brief_List(BaseModel):
	"""
	Created at the course planning stage.
	"""
	course_briefs: List[Course_Brief]

class SME(BaseModel):
	"""
	Created at the SME generation stage.
	"""
	persona: str

class Course_Skills(BaseModel):
	"""
	Created at the skill mapping stage.
	"""
	skills: List[str]

class TOC_Chapter(BaseModel):
	"""
	Created at TOC stage.
	"""
	title: str
	sections: List[str]

class TOC(BaseModel):
	"""
	Created at TOC stage.
	"""
	chapters: List[TOC_Chapter]

class Content_Section(BaseModel):
	"""
	Created at Content creation stage.
	"""
	title: str
	content: str

class Content_Chapter(BaseModel):
	"""
	Created at Content creation stage.
	"""
	title: str
	content: List[Content_Section]

class Learning_Objectives_Section(BaseModel):
	"""
	Created at the learning objective creation stage.
	This is a string containing the learning objectives for a given Section of a course.
	"""
	section_title: str
	learning_objectives: str

class Learning_Objectives_Chapter(BaseModel):
	"""
	Created at the learning objective creation stage.
	This is a list of Learning_Objectives_Section objects.
	"""
	title: str
	sections: List[Learning_Objectives_Section]

class Learning_Objectives_Course(BaseModel):
	"""
	Created at the learning objective creation stage.
	This is a list of Learning_Objectives_Chapter objects.
	"""
	chapters: List[Learning_Objectives_Chapter]

class Content_Section(BaseModel):
	"""
	Created at the content creation stage.
	"""
	title: str
	content: str

class Content_Chapter(BaseModel):
	"""
	Created at the content creation stage.
	"""
	title: str
	content: List[Content_Section]

class Content(BaseModel):
	"""
	Created at the content creation stage.
	"""
	chapters: List[Content_Chapter]

class Course(BaseModel):
	"""
	This is the wrapping Course object, which is created along the way.
	We are not asking LLMs to generate this.
	Making these field optional as this object is slowly built up.
	"""
	brief: Optional[Course_Brief] = None
	sme: Optional[SME] = None
	skills: Optional[Course_Skills] = None
	toc: Optional[TOC] = None
	learning_objectives: Optional[Learning_Objectives_Course] = None
	content: Optional[Content] = None
	text: Optional[str] = None
	
	# We want to validate upon assignment, not just on initialization.
	class Config:
		validate_assignment = True

# Our functions

def convert_course_content_to_txt(course: Course) -> str:
	"""
	Converts the course content to a text string.
	"""
	course_text = ""
	course_text += f"# {course.brief.title}\n"
	for chapter in course.content.chapters:
		print(f"\n## {chapter.title}")
		course_text += f"## {chapter.title}\n"
		for section in chapter.content:
			print(f"\t# {section.title}")
			course_text += section.content
	return course_text

# Our chains

def create_course_briefs(model = 'gpt') -> Course_Brief_List:
	"""
	With no input, Managing Editor comes up with the catalog.
	"""
	print("Managing Editor designs 50 course briefs...")
	model = Model(model)
	prompt = Prompt(course_planning_prompt)
	parser = Parser(Course_Brief_List)
	chain = Chain(prompt, model, parser)
	response = chain.run()
	return response.content.course_briefs

def create_sme_prompt(course: Course, model = 'gpt') -> SME:
	"""
	With the course briefs, we generate the SME prompts.
	"""
	print("Creating SME prompt...")
	input_variables = vars(course.brief)
	prompt = Prompt(SME_metaprompt)
	model = Model(model)
	parser = Parser(SME)
	chain = Chain(prompt, model, parser)
	response = chain.run(input_variables = input_variables)
	return response.content

def create_course_skills(course: Course, model = 'gpt') -> Course_Brief:
	"""
	With the course briefs, we generate the course skills.
	"""
	print("Generating course skills...")
	input_variables = vars(course.brief)
	prompt = Prompt(course_skills_prompt)
	model = Model(model)
	parser = Parser(Course_Skills)
	chain = Chain(prompt, model, parser)
	response = chain.run(input_variables = input_variables)
	return response.content

def create_toc(course: Course, model = 'gpt') -> TOC:
	"""
	With the course briefs, we generate the TOCs.
	"""
	print("Our SME is creating TOC...")
	input_variables = {'title': course.brief.title, 'audience': course.brief.audience, 'skills': course.skills.skills, 'persona': course.sme.persona, 'course_format': course_format}
	prompt = Prompt(toc_creation_prompt)
	model = Model(model)
	parser = Parser(TOC)
	chain = Chain(prompt, model, parser)
	response = chain.run(input_variables = input_variables)
	return response.content

def create_learning_objectives(course: Course, section: str, previous_section = None, model = 'gpt3') -> Learning_Objectives_Section:
	"""
	With the brief and the course skills, generate the learning objectives for a section.
	This should provide an example of the previous section if available.
	"""
	input_variables = {'title': course.brief.title, 'audience': course.brief.audience, 'skills': course.skills.skills, 'toc': course.toc, 'section_title': section, 'previous_section': previous_section, 'course_format': course_format}
	prompt = Prompt(learning_objectives_prompt)
	model = Model('gpt3')
	parser = Parser(Learning_Objectives_Section)
	chain = Chain(prompt, model, parser)
	response = chain.run(input_variables = input_variables)
	return response.content

def create_learning_objectives_course(course: Course, model = 'haiku', cap = None) -> Learning_Objectives_Course:
	"""
	Wrapper function.
	With the course briefs, we generate the learning objectives.
	"""
	learning_objectives_toc = []
	for index, chapter in enumerate(course.toc.chapters[:cap]):
		print(f"Creating learning objectives for chapter {index+1}...")
		chapter_title = chapter.title
		learning_objectives_chapter = []
		for index, section in enumerate(chapter.sections):
			print(f"\tCreating learning objectives for section {index+1}...")
			learning_objectives = create_learning_objectives(course = course, section=section, previous_section=learning_objectives_toc[-1] if learning_objectives_toc else None, model = model)
			learning_objectives_chapter.append(learning_objectives)
		learning_objectives_toc.append(Learning_Objectives_Chapter(title = chapter_title, sections = learning_objectives_chapter))
	return Learning_Objectives_Course(chapters = learning_objectives_toc)

def create_learning_objectives_course_async(course: Course, model = 'gpt3', cap = None) -> Learning_Objectives_Course:
	"""
	Wrapper function.
	With the course briefs, we generate the learning objectives.
	"""
	# Generate the prompts; we will run these asynchronously
	prompt_dicts = []
	for index, chapter in enumerate(course.toc.chapters[:cap]):
		for index, section in enumerate(chapter.sections):
			prompt_dict = {}
			print(f"\tCreating learning objectives prompts for section {index+1}...")
			learning_objectives_prompt = create_learning_objectives_prompt(course = course, section=section, model = model)
			prompt_dict['section_title'] = section
			prompt_dict['prompt'] = learning_objectives_prompt
			prompt_dicts.append(prompt_dict)
		# Run the prompts asynchronously
		prompts = [prompt_dict['prompt'] for prompt_dict in prompt_dicts]
		model = Model(model)
		results = model.run_async(prompts, pydantic_model = Learning_Objectives_Section, verbose = True)
		print("Results:", results)
		# Process results as a structured learning objectives course object
		learning_objectives_toc = []
		for index, chapter in enumerate(course.toc.chapters[:cap]):
			chapter_title = chapter.title
			learning_objectives_chapter = []
			for index, section in enumerate(chapter.sections):
				learning_objectives = results[index]
				learning_objectives_chapter.append(learning_objectives)
			learning_objectives_toc.append(Learning_Objectives_Chapter(title = chapter_title, sections = learning_objectives_chapter))
		# Return results
	return Learning_Objectives_Course(chapters = learning_objectives_toc)

def create_learning_objectives_prompt(course: Course, section: str, model = 'gpt3') -> Learning_Objectives_Section:
	"""
	With the brief and the course skills, generate the learning objectives for a section.
	This should provide an example of the previous section if available.
	"""
	input_variables = {'title': course.brief.title, 'audience': course.brief.audience, 'skills': course.skills.skills, 'toc': course.toc, 'section_title': section, 'course_format': course_format}
	prompt_template = Prompt(learning_objectives_prompt)
	prompt = prompt_template.render(input_variables = input_variables)
	return prompt

def write_section(course: Course, section: Learning_Objectives_Section, previous_section = None, model = 'gpt3') -> Content_Section:
	"""
	Given a course and a learning objectives section, write the content for that section.
	We will not use pydantic for the actual request here, since we will want to be flexible with models for testing / 
	the sheer scale of the course library.
	"""
	input_variables = {'persona': course.sme.persona, 'title': course.brief.title, 'audience': course.brief.audience, 'skills': course.skills.skills, 'toc': course.toc, 'section_title': section.section_title, 'learning_objectives': section.learning_objectives, 'previous_section': previous_section, 'course_format': course_format, 'content_instructions': course_writing_instructions}
	prompt = Prompt(content_writing_prompt)
	model = Model(model)
	chain = Chain(prompt, model)
	response = chain.run(input_variables = input_variables)
	return Content_Section(title = section.section_title, content = response.content)

def create_content(course: Course, model = 'haiku', cap = None) -> Content:
	"""
	Wrapper function.
	Given a learning_objectives_course object, generate the content for the entire course.
	"""
	course_content = []
	for index, learning_objectives_chapter in enumerate(course.learning_objectives.chapters):
		print(f"Writing content for chapter {index+1}...")
		chapter_content = []
		for index, section in enumerate(learning_objectives_chapter.sections[:cap]):
			print(f"\tWriting content for section {index+1}...")
			content_section = write_section(course, section, previous_section = chapter_content[-1] if chapter_content else None, model = 'gpt3')
			chapter_content.append(content_section)
		course_content.append(Content_Chapter(title = learning_objectives_chapter.title, content = chapter_content))
	return Content(chapters = course_content)

def create_course_from_brief(brief: Course_Brief, cap = None) -> Course:
	"""
	Wrapper function.
	With the course briefs, we generate the course.
	"""
	course = Course()
	course.brief = brief
	course.sme = create_sme_prompt(course)
	course.skills = create_course_skills(course)
	course.toc = create_toc(course)
	# course.learning_objectives = create_learning_objectives_course(course, cap = cap)
	course.learning_objectives = create_learning_objectives_course_async(course, cap = cap)
	course.content = create_content(course, cap = cap)
	course.text = convert_course_content_to_txt(course)
	return course

if __name__ == "__main__":
	print("Dreaming up the ideal course library...")
	course_briefs = create_course_briefs()
	print("Picking one course:")
	brief = random.choice(course_briefs)
	course = create_course_from_brief(brief) # set cap = 2 to throttle this for testing purposes; remove cap to create entire course. cap = number of chapters to create.
	print("=======================================================")
	for key in course.__dict__.keys():
		print(f"{key}: {course.__dict__[key]}")

"""
- async for wrapper functions
- save Course objects to a special Sophie collection in MongoDB
x - add preferred model to each function
x - create the object-> string function
x - incorporate the SME into the content writing
x - add a cap to each wrapper function
x - tighten up course length, wtf is this (15+ chapters??)
x - fix markdown styling within prompts + the final print function
"""

from Chain import Prompt, Model, Parser, Chain
from pydantic import BaseModel
from typing import List, Optional

class Objects(BaseModel):
	objects: List[str]

prompts = ['birds', 'mammals', 'presidents', 'planets', 'countries', 'cities']
prompt_template = Prompt("Name ten {{objects}}.")
prompts = [prompt_template.render(input_variables = {'objects': prompt}) for prompt in prompts]
model = Model('gpt3')
results = model.run_async(prompts, pydantic_model = Objects, verbose = False)


