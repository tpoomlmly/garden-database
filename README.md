Analysis
========

Background to problem
---------------------

Professional gardeners need a way to manage their many clients and the various
plants that they all own. Each type of plant requires to be tended to during
different seasons and in different ways, and all this needs to be memorised and
managed. For example, Wisteria needs to be cut twice in the year – once at the
end of the summer and again in the winter – to maximise the number of flowers.
Another example would be roses; rambling roses should be pruned at the end of
the summer and climbing roses have to be pruned in late autumn. It can be
difficult to tell the two apart and if there is more than one gardener working
at a client then it is good to have a record of which rose is which.

It is currently difficult to remember the plants that each client has because
they may have over one hundred different species in their garden. This makes
planning the maintenance that needs to be done each month extremely complicated.
Knowing what needs to be done and when means that the right tools for the job
can be taken each day.

Currently available solutions
-----------------------------

The end user’s current system in place uses a paper record. This consists of a
calendar created in Microsoft Word for each client, with the maintenance for
each month written on it. Each time there is a new client, a new calendar has to
be created. A list of all of their plants is cross-referenced with a book
containing the monthly maintenance required for each type of plant and the
calendar is filled in. Whenever a client buys a new plant, the paper calendar
has to be updated to account for this. This is a very tedious process, which
could be simplified if the need to re-write everything for every new client was
removed. There is currently no software solution in existence designed
specifically for this problem, but there are custom database creation and
frontend programs available such as Ninox and Filemanager Pro. These programs
allow the user to create databases with frontends that suit their needs, but
they are very complicated to set up and it would be difficult for the end user
to customise the eventual interface to be exactly to their needs. These programs
also have the downside of being purely digital. In other situations, it may not
make a difference whether the data is kept on paper or on a smartphone, however
in a garden there is nowhere to charge a portable device and it would be
catastrophic if access to data was lost.

Description of solution
-----------------------

My project will be a database with a web front-end, allowing the end user to add
and remove clients, plants and jobs that each plant needs doing. The data will
be organised in a coherent way, so that the end user can see a breakdown of the
maintenance required per client per month. The project will be web-based using
Python and Flask and will be hosted on a remote server to enable it to be
accessed from anywhere. The end user will be able to add, edit and remove
clients, plants and maintenance jobs via an HTML form. Clients will be able to
have plants assigned to them and plants will be able to have maintenance
assigned to them by month. On the client page, when a client and month are
selected, a full breakdown of the maintenance required for all that client’s
plants for that month is shown. This will be printable so that a paper copy can
be taken to the client for reference instead of having to rely on a mobile
phone. On the maintenance page, a list of all created maintenance jobs will be
shown, with a form to add a new job. In this form there will be options to
select the plants that this maintenance applies to, if any yet. The plants page
will contain a list of all plants in the database and all their information, as
well as which clients own them and what maintenance each plant has for each
month.

Interview with end user
-----------------------

My end user is Sue Poll, who is a professional gardener and specifically
requested this software to be made.

**Q:** What kind of functionality were you looking for? What kind of data are
you looking to be able to store?

**A:** I’d like to be able to have a list of clients that shows the plants that
they own, and all the maintenance that needs to be done in the current month.
I’d like to be able to look at a plant and see its maintenance broken down per
month, and the clients that own that plant.

**Q:** Would it be useful to be able to record the cost of plants?

**A:** No – because I want the database to be about managing the maintenance of
the plants; invoicing customers for products and services is a separate issue.

**Q:** Would it be useful to have both the common name and Latin name of the
plants?

**A:** It would, very much, yes.

**Q:** What system do you currently use to manage the plants that each client
has and the jobs that need doing each time you garden for them?

**A:** I use the lesson plan template on Microsoft Word that I have customised
for each month for each client. I have a separate list for the plants in each
garden on paper and I use information from books and the internet to work out
what the maintenance needs are for each month.

**Q:** How would you like the information to be set out on the page?

**A:** Some databases that I have seen look a bit like an Excel spreadsheet and
I find that quite difficult to scan through easily, so I suppose I prefer the
information to be in more of a Word document style, like a list. I have used
Filemaker Pro and found the screens where you put the data in quite easy to use;
the search facility was also very effective. The screens where you input data
could be quite boxy, but the output would need to be more like a Word document.
In my current solution I have headings for each plant category such as bulbs,
shrubs and climbers. At the moment this is very general, and I would like it to
be more specific – I want it to show the information for each plant instead of
each category.

**Q:** Would you like a page where you can select a client that will produce a
maintenance plan?

**A:** Yes, I would like to be able to select a client and a month, and have a
plan specific to that client for that month generated.

**Q:** What plant information would you like to include?

**A:** The Latin name, the common name (though some plants have lots of common
names so this is not necessarily helpful) and the blooming period. A photo would
be useful, but too many photos tend to make databases run slowly. It’s not
essential unless the plant is really unusual.

**Q:** Will multiple plants have the same maintenance, or will the maintenance
be different for each plant?

**A:** Multiple plants will have the same maintenance, for example, many
perennials are cut back at the same time in early autumn and don’t need anything
else doing to them for the rest of the year. Many fruit trees are pruned at the
same time, but not in the same way.

**Q:** Do some plants require the same maintenance in some months but have
different needs in others?

**A:** Perhaps it would be more useful for each plant to have a dropdown list
for tasks to be carried out each month when putting the information into the
database so that you can choose from prune, or mulch, or feed, or plant for
example.

**Q:** Do you want the maintenance to be entered on a plant-by-plant basis, or
be able to enter the maintenance on a separate page and then choose a
maintenance job to assign to a plant when the plant is created?

**A:** I want to enter a plant, and when I enter that plant I want to be able to
assign a maintenance to it for each month. Instead of clicking on a client which
takes me to a list of plants which I can click on for a list of maintenance, I
would like to be able to click on a client to get a list of months, which lead
to all the plants and their maintenance for that client in that month. It would
be useful if it was printable as well.

**Q:** How useful would it be to have the program automatically go to the
current month?

**A:** I would rather have it just highlight the current month. I usually plan
for the month ahead at the end of the current one.

User requirements
-----------------

1.  A page for displaying clients that allows the end user to select a client
    and a month, to bring up a list of that month’s maintenance for all the
    plants that the client owns

2.  The ability to print this page in a useful format

3.  The ability to add, edit and delete client information and decide what
    plants a client has when adding or editing the client’s entry

4.  A page for displaying plants including their name, Latin name and blooming
    period that allows the end user to add, edit and delete plant information
    and select what maintenance each plant needs each month; possibly also a
    photo of each plant if the speed penalty is not too great

5.  A page with a list of maintenance jobs showing a name, a text description
    and the month that that job pertains to with the ability to add, edit and
    delete entries

6.  An easy-to-use, abstract interface that disguises the technical aspects of
    databases

SMART objectives
----------------

1.  To have a database file that is generated and initialised when the if it
    does not already exist

    1.  To have a table for clients storing their name

    2.  To have a table for plants storing their common name, scientific name
        and blooming period

    3.  To have a table for maintenance jobs storing a name, job description and
        the month it applies to

    4.  To have a plant-maintenance junction table linking plant IDs to the IDs
        of the maintenance that they require

    5.  To have a client-plant junction table linking client IDs to the IDs of
        the plants that they own

    6.  To have code that uses the junction tables to enforce many-to-many
        relationships between the clients and plants, and the plants and
        maintenance

2.  To have a graphical user interface

    1.  To have a Flask-based web server

    2.  To have a webpage showing a list of plants

        1.  To have a button that opens a dialogue box that allows the user to
            add a new plant with all its details including: its common name, its
            scientific name and the jobs that need doing to it

        2.  To allow the user to click on a client or a job in this list and
            view their database entry

    3.  To have a webpage showing a list of clients

        1.  To have a button that opens a dialogue box that allows the user to
            add a new client with all their details including their name and the
            plants they own

        2.  To allow the user to click on a plant in this list and view its
            database entry

        3.  To have sets of radio buttons allowing the user to select a client
            and a month, to bring up a list of all the maintenance, categorised
            by plant, for that client and month

        4.  To have a button that allows the user to print this list, without
            printing the functional parts of the webpage

    4.  To have a webpage showing a list of maintenance jobs

        1.  To have a button that opens a dialogue box that allows the user to
            add a new job with all of its details including: a title, a brief
            description and the month that this job needs doing in.

    5.  To have buttons on these pages allowing the user to delete and to edit
        items in these lists

    6.  To use Bootstrap to make the webpages look aesthetically pleasing and
        provide the interactive functionality
