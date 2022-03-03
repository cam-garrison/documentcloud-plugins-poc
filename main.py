"""
This is a metadata scraping plugin for DocumentCloud.

It demonstrates how to write a add-on which can be activated from the
DocumentCloud add-on system and run using Github Actions.  It receives data
from DocumentCloud via the request dispatch and writes data back to
DocumentCloud using the standard API
"""
from addon import AddOn
import csv


class MetadaScrape(AddOn):
    """An metadata scraping Add-On for DocumentCloud."""

    def main(self):
        """The main add-on functionality goes here."""
        #fetch your add-on specific data
        #name = self.data.get("name", "world")

        self.set_message("Beginning metadata scraping!")

        # preset header + metadata list
        header = ['id', 'title', 'privacy level', 'asset-url', 
        'contributor', 'created at date', 'description' ,'full text url', 'pdf url',
        'page count', 'Tags', 'Key Value Pairs']
        metadata_list = [] # list o lists containing metadata for each document

        #takes the document object and an empty array as input, and places the document metadata into the array
        def setData(doc, doc_metadata):

            #document description break fix
            try:
                description = doc.description
            except AttributeError:
                 description = ""
            
            doc_metadata = [doc.id, doc.title, doc.access, doc.asset_url,
            doc.contributor, doc.created_at, description, doc.full_text_url,
            doc.pdf_url, doc.page_count]

            #separate key values and tags into two separate arrays
            keyvalues = doc.data
            tags = ""

            #are there any tags?
            try:
                tags = keyvalues['_tag']
                del keyvalues['_tag']
            except KeyError:
                tags = ""
            
            doc_metadata.append(tags)
            doc_metadata.append(keyvalues)

            return doc_metadata

        # retrieve information from each document.
        description = "NO DESCRIPTION PRESENT" #for the edge case with the description not existing
        if self.documents:
            length = len(self.documents)
            for i, doc_id in enumerate(self.documents):
                self.set_progress(100 * i // length)
                doc = self.client.documents.get(doc_id)

                #set the metadata
                metadata_list.append(setData(doc,[]))
        elif self.query:
            documents = self.client.documents.search(self.query)
            length = len(documents)
            for i, doc in enumerate(documents):
                self.set_progress(100 * i // length)
                
                #set the metadata
                metadata_list.append(setData(doc,[]))

        # the id of the first document + how many more documents will be the name of the file
        try:
            firstTitle = metadata_list[0][1]
        except IndexError:
            firstTitle = ""
            length = 1

        with open("metadata_for-"+str(firstTitle)+"-_+"+str(length-1)+".csv", "w+") as file_:
            writer = csv.writer(file_)

            #FORMAT HEADER
            writer.writerow(header)

            for row in metadata_list:
                #FORMAT THE DATA 
                writer.writerow(row)
            
            self.upload_file(file_)

        self.set_message("Metadata scraping end!")
        # self.send_mail("Hello World!", "We finished!")


if __name__ == "__main__":
    MetadaScrape().main()
