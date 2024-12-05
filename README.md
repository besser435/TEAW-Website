# TEAW-Website
 
## Git Info
There are two branches, `prod` and `dev`. The default is `dev`, and where any changes should be made. 

Currently since we are in the dev phase, any changes made to dev will cause the GH Action to be ran, 
updating the site with whatever is on the repo. 

In the future, changes will be deployed by bring changes over from dev (or some other branch) to prod using a pull request.
Only once approved, will the PR be merged, and the new changes deployed. This will help
with security to ensure someone doesnt RCE me, and to ensure the website is kept clean and functional.
