# Read Me
## Collin Martin | 100503980
## Noa Dori | 

## Additional Functionality
The use of JavaScript for the filters in `index.html` while in `Dashboard section`. This is an event listener that is a real time selection so no form needs to be submitted. It rather listens for a change in any of these fields than automatically submits form.

 Later it is grabbed by the controller using request.args.get() instead of request.form which is different from what we have seen in any of the lectures and was found by using external resources for javascript documentation. This is also used for viewing new, joined, or all trips within the same page. 


The use of Javascript to switch between different divs (dates| Ranged or Fixed) present within the html within `edit_trip.html` and within `create_trip.html`

The implementation of Profile avatars.

The addition of 3 optional Stops to the trip which is the final place a user can go. This is where the users mainly put up suggestions and hte name of the restaurants. Instead of 1 big trip we added this to make it more of an event rather than a dinner/breakfast/... Like a pub crawl.

We are a group of two so we were limited on time and couldn't dive deep into funcitonality additions. We wanted to add invitations to trips and following functionality but didn't get to it. Perhaps we will keep working on it to add them when the project is over.

# Testing the Web Application
To test it would be easiest to sign in with this Username and Password we have provided below.

# Declaration of AI tools
Yes we used Artificial intelligence.
The use of AI tools was used for questioning about specific use of jinja templates, errors we had trouble finding or understanding, and also to implement few things we deemed out of our reach. For these implementations we used Claude Sonnet 4 and 4.5 to help us with the coding and understanding process.
1. The code we earlier deemed out of our reach or expertise was the use of stops as a list within create and edit_trip. Here we used the following code presented by an LLM `stops[{{ i }}][stop_id]`. After we received and idea of the correct syntax we typeb by hand from their. This was the approach for very few other items. Find the syntax (Correct way) and implement it ourselves so we won't have to ask it the question again. 
2. Help with AI understanding FlexBox. this is a css layout that worked for us because we have many side by side items we didn't want fixed in certain locations. So to find our how to make our divs use ratios of the total width AI assisted us in choosing and implementing some of the flex box divs. The most relavent place for this is inside trips.html as the ratio mattered there. For this we also used documentation from CSS-Tricks to get us as far as we could. 
3. Finding and Understanding certain errors. After exhausting our search for the error or could not understand why we were getting an error in some places. We would sometimes use AI to help find or interpret an error to fix or fix our selves. Most of these errors were within the Model building stage and population of the DB since most of the errors give one line statement with no context. Later in the project when making html code, a div or span would be incorrectly written and later solved by chat gpt because we put the element in the wrong place or it is missing a / in our closing div. Simple errors.
4. Finally, we used AI to populate our model for testing. Prompting the AI to populate our database saved us tons of time. This is because we used a local DB using Docker that is shared between us. So a test_script.py was generated to populate the database for every launch of our web application.




