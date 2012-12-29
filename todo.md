ToDo
##############

- make slug a list to allow renaming/multiple slugs (still unique?) Or slugs = ListField(StringField()) for when there are multiple?

- sequential field is using base d collection, should be cnts, etc

- load yaml sys data on start, langs, countries, us states, zip codes

- limit length of slug and do not split on word.

- babel

- trash, cascade?

- view hierarchy 
	mock up usecase like:
		Prj.sow_what: Sow What
			Description: bla bla
			Date: some date
			Etc:
			- Note.slug: Note Title
				Body of note
				- Cmnt.slug: Comment Title
					Author: ____, Date: ____
					Comment Body
					- Cmnt.slug: Reply to Comment
						Author: ____, Date: ____
						Comment Body
			- Exp.slug: Experience Title
				Description: ___
				Etc: ____
				- Note.slug: Note Title
					Body of note
				- Cmnt.slug: Reply to Comment
					Author: ____, Date: ____
					Comment Body
										
- recycle trashed items

- general tagging





