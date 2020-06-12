from flask import Flask, render_template, request, send_file
import pandas
from geopy.geocoders import ArcGIS
from werkzeug.utils import secure_filename

geo = ArcGIS()
app=Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/success-table", methods=['POST'])
def success():
    global file
    if request.method == 'POST':
        file = request.files["file"]
        upload=secure_filename("uploaded_" + file.filename)
        file.save(upload)
        # import the upload into a pandas dataframe 
        df=pandas.read_csv(upload)
        add_cols = [col for col in df.columns if col == "Address" or col == "address"]
        # check to see if the list contains any results
        if add_cols:
            # if it does, check for a lower case address and change to title case
            if add_cols[0] == "address":
                df.rename(columns={"address" : "Address"}, inplace=True)
        # otherwise, if the list is empty return an error to the user that they need an address column in their file
        else:
            return render_template("index.html",
            text="Please ensure you have a column titled 'Address' or 'address' in your upload CSV file.")
        # populate both the latitude and longitude in the dataframe for the supplied addresses
        df["Latitude"] = df["Address"].apply(lambda lat: geo.geocode(lat).latitude if lat !=None else None)
        df["Longitude"] = df["Address"].apply(lambda lon: geo.geocode(lon).longitude if lon !=None else None)
        # export the dataframe as a CSV file
        df.to_csv("dl.csv", index=False)
        # display the dataframe, including lat / lon data, on the page and provide a download button
        return render_template("index.html", text=df.to_html(justify="left", classes="mystyle"), btn="download.html")

@app.route("/download")
def download():
    # provides the CSV version of the dataframe to the user as a download called "your_download.csv"
    # cache_timeout is *very* important as if it is not set to zero, the browser will default to keeping the last file
    #  downloaded cached for around 12 hours. Setting this to zero is the only way to avoid having the same data be
    #  provided for download constantly for 12 hours.
    return send_file("dl.csv", attachment_filename="your_download.csv", as_attachment=True, cache_timeout=0)

if __name__ == "__main__":
    # set app.debug to False for a production version.
    app.debug=False # set this to True in dev environment
    app.run()
