"""
Experimenting with generating PromptFlow objects from the Publishing Philosophy that we generated in the Sophie Cannoli.
"""
from pydantic import BaseModel
from Chain import Chain, Model, Prompt, Parser
from typing import List, Optional
import random

natural_language_description = """
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

They will have three parts of their library:
- leadership and management courses
- soft skills courses (like Negotiation, Communication, Presentation Skills, etc.)
- business function courses
- technical skills courses (software development and IT)

They leverage SMEs to create the content, and have a team of instructional designers to create the course structure.
There is also a team of content writers, editors, QA specialists, and a managing editor.

We want a workflow that takes a course title as input and outputs a completed course.
""".strip()

course_format = """
- **Total Chapters**: 6-8

The first Chapter should be titled "Introduction", and be composed of two sections:
1. an overview of the course objectives and structure, with an evocative title that captures
the value proposition of the course for the learner.
2. a section titled "Who this course is for" which sets the right expectations for the learner.

The last Chapter should be titled "Conclusion", and have two sections:
1. a "Conclusion" section providing a pithy summary of the course content and key takeaways
2. a "Next Steps" section with suggestions for further learning or practice

The remaining chapters are the body of the course.

- **Sections per Chapter**: 3-4 sections
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
- Leadership and Management (examples: becoming a manager, organizational leadership, strategic planning): 20% of courses
- Professional Development (examples: interpersonal communication, negotiation, executive presence): 15% of courses
- Business Functions (examples: Marketing, Sales, Finance): 15% of courses
- Business software (examples: Excel, SAP, Salesforce): 10% of courses
- Software development (examples: Java development, web development. machine learning) 20% of courses
- IT administration (examples: linux administration, database administration, network engineering) 20% of courses
""".strip()

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
You are an expert prompt engineer specializing in educational content creation.
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

The company you work for produces text-baseed courses in this format:
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
""".strip()

learning_objectives_prompt = """
You are an instructional designer who has extensive experience in both higher ed and the corporate training
and learning and development worlds. You make strong use of the Understanding by Design (UbD) framework
and can apply it to a variety of domains in collaboration with subject matter experts to create impactful
text-based courses.

The courses you create are text-based, hosted online, and are aimed at large enterprises looking to upskill
employees. These courses are expertly designed to both help companies fill important skill gaps to improve performance
as well as providing tangible career advice to employees.

The company you work for produces text-baseed courses in this format:
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

Here are the learning objectives for the previous section for reference:
{{previous_section}}

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

content_prompt = """
2. Outline best practices for course creation, including:
   - Structuring content for optimal learning
   - Engaging presentation techniques
   - Incorporating practical examples and case studies
   - Addressing diverse learning styles

3. Provide guidelines for ensuring course quality:
   - Accuracy and up-to-date information
   - Clarity and conciseness in explanations
   - Logical flow and progression of ideas
   - Appropriate depth and breadth of content

4. Suggest methods for incorporating the specified skills:
   - Integrating skill development throughout the course
   - Providing opportunities for practical application
   - Assessing skill acquisition

5. Emphasize the importance of:
   - Learner-centric approach
   - Inclusive and accessible content
   - Ethical considerations relevant to the field
""".strip()

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
	text = f"Course Title: {course.brief.title}\n\n"
	text += f"Audience: {course.brief.audience}\n\n"
	text += f"Skills: {course.brief.skills}\n\n"
	text += "Table of Contents\n\n"
	for chapter in course.toc.chapters:
		text += f"{chapter.title}\n"
		for section in chapter.sections:
			text += f"  - {video}\n"
	text += "\nCourse Content\n\n"
	for chapter in course.content.chapters:
		text += f"{chapter.title}\n"
		for section in chapter.content:
			text += f"  - {section.title}\n"
			text += f"    {section.content}\n"
	return text

# Our chains

def create_course_briefs() -> Course_Brief_List:
	"""
	With no input, Managing Editor comes up with the catalog.
	"""
	model = Model('gpt')
	prompt = Prompt(course_planning_prompt)
	parser = Parser(Course_Brief_List)
	chain = Chain(prompt, model, parser)
	response = chain.run()
	return response.content.course_briefs

def create_sme_prompt(course: Course) -> SME:
	"""
	With the course briefs, we generate the SME prompts.
	"""
	print("\n\nCreating SME prompt...\n\n")
	input_variables = vars(course.brief)
	prompt = Prompt(SME_metaprompt)
	model = Model('gpt')
	parser = Parser(SME)
	chain = Chain(prompt, model, parser)
	response = chain.run(input_variables = input_variables)
	return response.content

def create_course_skills(course: Course) -> Course_Brief:
	"""
	With the course briefs, we generate the course skills.
	"""
	print("\n\nGenerating course skills...\n\n")
	input_variables = vars(course.brief)
	prompt = Prompt(course_skills_prompt)
	model = Model('gpt')
	parser = Parser(Course_Skills)
	chain = Chain(prompt, model, parser)
	response = chain.run(input_variables = input_variables)
	return response.content

def create_toc(course: Course) -> TOC:
	"""
	With the course briefs, we generate the TOCs.
	"""
	print("\n\nOur SME is creating TOC...\n\n")
	input_variables = {'title': course.brief.title, 'audience': course.brief.audience, 'skills': course.skills.skills, 'persona': course.sme.persona, 'course_format': course_format}
	prompt = Prompt(toc_creation_prompt)
	model = Model('gpt')
	parser = Parser(TOC)
	chain = Chain(prompt, model, parser)
	response = chain.run(input_variables = input_variables)
	return response.content

def create_learning_objectives(section: str, previous_section = None) -> Learning_Objectives_Section:
	"""
	With the brief and the course skills, generate the learning objectives for a section.
	This should provide an example of the previous section if available.
	"""
	input_variables = {'title': course.brief.title, 'audience': course.brief.audience, 'skills': course.skills.skills, 'toc': course.toc, 'section_title': section, 'previous_section': previous_section, 'course_format': course_format}
	prompt = Prompt(learning_objectives_prompt)
	model = Model('gpt')
	parser = Parser(Learning_Objectives_Section)
	chain = Chain(prompt, model, parser)
	response = chain.run(input_variables = input_variables)
	return response.content

def create_learning_objectives_course(course: Course) -> Learning_Objectives_Course:
	"""
	Wrapper function.
	With the course briefs, we generate the learning objectives.
	"""
	learning_objectives_toc = []
	for chapter in course.toc.chapters[:1]:
		chapter_title = chapter.title
		learning_objectives_chapter = []
		for section in chapter.sections:
			learning_objectives = create_learning_objectives(section=section, previous_section=learning_objectives_toc[-1] if learning_objectives_toc else None)
			learning_objectives_chapter.append(learning_objectives)
		learning_objectives_toc.append(Learning_Objectives_Chapter(title = chapter_title, sections = learning_objectives_chapter))
	return Learning_Objectives_Course(chapters = learning_objectives_toc)

def create_content(course: Course) -> Content:
	"""
	With the course briefs, we generate the content.
	"""
	pass

def create_course_from_brief(brief: Course_Brief) -> Course:
	"""
	Wrapper function.
	With the course briefs, we generate the course.
	"""
	# course = Course()
	# course.brief = brief
	# course.sme = create_sme_prompt(course)
	# course.skills = create_course_skills(course)
	# course.toc = create_toc(course)
	# course.learning_objectives = create_learning_objectives(course)
	# course.content = create_content(course)
	# course.text = convert_course_content_to_txt(course)
	# return course
	pass

# if __name__ == "__main__":

print ("Dreaming up the ideal course library...\n\n")
course_briefs = create_course_briefs()
print("\n\nPicking one course:\n\n")
brief = random.choice(course_briefs)

# our course which will be built up.
course = Course()

# Working with one brief to create our create_sme_prompt function.
# brief = Course_Brief(title='Digital Marketing 101', audience='Marketing professionals looking to understand digital channels.', skills='SEO, SEM, Social Media Marketing, Email Marketing.')
# add to course object
course.brief = brief
print(course.brief)

# our SME creation phase
course.sme = create_sme_prompt(course)
print(course.sme)

# Working with one sme to create our create_course_skills function.
# sme = SME(persona="You are an experienced digital marketing professional and educator. You have a Master's degree or Ph.D. in Marketing, Communications, or a related field. You possess over 10 years of experience in digital marketing, having worked in various high-impact roles such as Digital Marketing Manager, SEO Expert, or Social Media Strategist. Your notable achievements include leading successful digital marketing campaigns for well-known brands, contributing to significant increases in online engagement and sales, or receiving industry awards for innovative digital marketing strategies.\n\nIn addition to your professional experience, you have over 5 years of teaching or mentoring experience. You have taught digital marketing courses at universities or professional training programs, receiving positive feedback from students for your engaging and practical teaching methods. Your teaching philosophy is centered around practical, hands-on learning, using real-world examples and case studies to illustrate key concepts. You believe in fostering a collaborative learning environment where students are encouraged to share their experiences and learn from one another.\n\nTeaching digital marketing to marketing professionals presents unique challenges, such as the rapidly changing nature of digital channels and the varying levels of prior knowledge among students. It is crucial to stay updated with the latest trends and technologies and to create content that is accessible to both beginners and more experienced marketers.\n\nWhen creating training for marketing professionals, keep in mind the importance of practical application. Ensure that the course includes actionable insights and tools that students can immediately implement in their own work. Emphasize the integration of digital marketing into broader marketing strategies and the importance of measuring and analyzing results to continuously improve and adapt strategies.")
# course.sme = sme

# our course skills creation phase
course.skills = create_course_skills(course)
print(course.skills)

# Working with one course skills to create our create_toc function.
# skills = Course_Skills(skills=['Search Engine Optimization (SEO)', 'Content Marketing', 'Social Media Marketing', 'Email Marketing', 'Affiliate Marketing', 'Pay-Per-Click Advertising (PPC)', 'Web Analytics', 'Conversion Rate Optimization (CRO)', 'Digital Branding', 'Customer Journey Mapping', 'Influencer Marketing', 'Mobile Marketing', 'Video Marketing', 'E-commerce Marketing'])
# course.skills = skills

# our TOC creation phase
course.toc = create_toc(course)
print(course.toc)

# Working with one TOC to create our create_learning_objectives function.
# toc = TOC(chapters=[TOC_Chapter(title='Introduction', videos=['Welcome to Digital Marketing 101: Unlocking Your Online Potential', 'Who This Course is For']), TOC_Chapter(title='Search Engine Optimization (SEO)', videos=['Understanding SEO: The Basics', 'Keyword Research and Strategy', 'On-Page Optimization Techniques', 'Off-Page SEO: Building Backlinks', 'SEO Tools and Analytics']), TOC_Chapter(title='Content Marketing', videos=['The Power of Content Marketing', 'Creating High-Quality Content', 'Content Distribution Strategies', 'Measuring Content Success']), TOC_Chapter(title='Social Media Marketing', videos=['Introduction to Social Media Marketing', 'Building a Social Media Strategy', 'Creating Engaging Social Media Content', 'Social Media Advertising', 'Analytics and Reporting for Social Media']), TOC_Chapter(title='Email Marketing', videos=['Introduction to Email Marketing', 'Building Your Email List', 'Crafting Effective Email Campaigns', 'Email Marketing Automation', 'Analyzing Email Performance']), TOC_Chapter(title='Affiliate Marketing', videos=['Getting Started with Affiliate Marketing', 'Choosing the Right Affiliates', 'Creating a Successful Affiliate Program', 'Tracking and Measuring Success']), TOC_Chapter(title='Pay-Per-Click Advertising (PPC)', videos=['PPC Fundamentals', 'Keyword Selection for PPC', 'Creating Effective PPC Ads', 'PPC Campaign Management', 'Analyzing PPC Performance']), TOC_Chapter(title='Web Analytics', videos=['Introduction to Web Analytics', 'Setting Up Google Analytics', 'Key Metrics and Reports', 'Analyzing User Behavior', 'Using Data to Improve Marketing Efforts']), TOC_Chapter(title='Conversion Rate Optimization (CRO)', videos=['Fundamentals of CRO', 'A/B Testing and Multivariate Testing', 'Optimizing Landing Pages', 'Using Analytics to Drive CRO', 'CRO Tools and Techniques']), TOC_Chapter(title='Digital Branding', videos=['Building a Digital Brand', 'Creating a Brand Strategy', 'Brand Positioning and Messaging', 'Maintaining Brand Consistency Online', 'Measuring Brand Equity']), TOC_Chapter(title='Customer Journey Mapping', videos=['Understanding the Customer Journey', 'Creating Customer Personas', 'Mapping the Customer Journey', 'Touchpoints and Channels Analysis', 'Improving Customer Experience']), TOC_Chapter(title='Influencer Marketing', videos=['Introduction to Influencer Marketing', 'Finding the Right Influencers', 'Building Influencer Relationships', 'Measuring Influencer Marketing Success']), TOC_Chapter(title='Mobile Marketing', videos=['Overview of Mobile Marketing', 'Creating Mobile-Friendly Content', 'Mobile Advertising Strategies', 'Measuring Mobile Marketing Success']), TOC_Chapter(title='Video Marketing', videos=['The Importance of Video Marketing', 'Creating Compelling Video Content', 'Distributing Videos Effectively', 'Video Analytics and Performance Measurement']), TOC_Chapter(title='E-commerce Marketing', videos=['Introduction to E-commerce Marketing', 'Driving Traffic to Your E-commerce Site', 'Optimizing Product Pages', 'E-commerce Sales Funnel', 'Retargeting and Upselling Strategies']), TOC_Chapter(title='Conclusion', videos=['Conclusion: Key Takeaways from Digital Marketing 101', 'Next Steps for Your Digital Marketing Journey'])])
# course.toc = toc

# our learning objectives creation phase
course.learning_objectives = create_learning_objectives_course(course)
print(course.learning_objectives)

"""
- Next up:
x	- SME writes video notes
		- preseed with intro and conclusion video examples (introduction, who this is for, conclusion, next steps)
x		- this is done iteratively, so SME can see what was written before
x		- use some intermediate step from UbD (don't overthink this)
		- use a corpus of examples (synthetically constructed, use claude manually for this)
	- Instructional Designer writes the actual texts
		- preseed with intro and conclusion video examples (introduction, who this is for, conclusion, next steps)
		- use a corpus of examples (synthetically constructed, use claude manually for this)
		- this is done iteratively, so ID can see what was written before
	- Content is converted to text (using the function we already created)
	- Pretty print
"""

