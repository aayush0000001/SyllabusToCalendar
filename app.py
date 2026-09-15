import io
import json
import os
from core.calendar_integration import upload_to_calendar
from core.data_extraction import syllabus_ingestion
from core.data_parsing import extracted_data_parsing
from dotenv import load_dotenv
from flask import Flask,redirect,render_template,request,url_for,request,session,url_for

#load environment variables from the .env files
load_dotenv()

#initializing flash using current module name
app=Flask(__name__)

#assigning the secret key using value stored in environment variable
app.secret_key=os.environ.get("FLASK_SECRET_KEY")

#using @app.route decorator with GET and POST methods allowed such that flask checks those http method when '/' hits
@app.route("/",methods=["GET","POST"])
def index():

    #check if http request method is POST
    if request.method=="POST":

        #extract the uploaded file using submitted form
        pdf=request.files["syllabus"]

        #extract user-specified academic year from submitted form
        class_year= request.form["class_year"]

        #extracting raw text/records from syllabus PDF without writing to disk.
        records=syllabus_ingestion(io.BytesIO(pdf.read()))

        #storing parsed data returned from gemini after pdf ingestion
        parsed=json.loads(extracted_data_parsing(str(records),class_year))

        #storing the parsed event dictionary inside user's browser session temporarily
        session["parsed_events"]=parsed

        #render the index template and pass the list of extracted events to be displayed to the user for review
        return render_template("index.html",events=parsed.get("events",[]))
    return render_template("index.html")
#dedicated post route to handle adding the events to calendar after the user review.
@app.post("/add")
def add():
    #retrieving and removing the parsed event data from user session to clear memory
    parsed=session.pop("parsed_events",None)

    #if nothing in the session (refresh after success, or direct visit) so send back to the upload form
    if not parsed:
        return redirect(url_for("index"))

    upload_to_calendar(parsed)

    #counting number of events added for user feedback
    count=len(parsed.get("events",[]))

    #render index template showing the process was successful
    return render_template(
        "index.html",message=f"Added {count} events to your Google Calendar"
    )


if __name__ == "__main__":
    app.run(debug=True)
