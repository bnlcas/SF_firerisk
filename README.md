# README

(This file structure was borrowed from a template made for Kaggle, found here: https://github.com/mikezawitkowski/kaggle_filestructure)

Note that all the data files go into the `input` directory where you'll find a ``.gitignore` file that contains this:

      *
      !.gitignore

This is so that the file directory is checked in to github, but that none of those big freaking data files are included to bog down the repo. If you want those, you'll have to get them from other sources.


(TODO: Do we want to link to the latest versions of the files here?)

Please note that ~~Kaggle has~~ **some source sites where we get our data may have** specific rules against sharing of ~~competition~~ **their** data, and this repository ~~attempts~~ **should attempt** to abide by those rules **or terms of use, etc.** If you end up forking this repo and using git to save your ~~competition~~ script file changes, but git doesn't see your file, you may want to check the `.gitignore` file to be certain it is configured to suit your purposes.


## Directory Structure

   - `input`: this contains all of the data files for the competition
   - `working`: on Kaggle, scripts run with this as the working directory. We recommend you do the same thing locally to avoid mixing output files with source files.
   - `src`: Source scripts. We've provided some examples to get you started.


## Command Line Execution

In your shell, you can navigate to the `working` directory, and run a script by saying:

`python ../src/your_fancy_script.py`

Then open `working/output.html` to view the results!
