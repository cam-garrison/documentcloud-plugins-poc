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
        # fetch your add-on specific data
        name = self.data.get("name", "world")

        self.set_message("Beginning metadata scraping!")

        # preset header + metadata list
        header = ['id', 'title', 'privacy level', 'asset-url', 
        'contributor', 'created at', 'description' ,'full text url', 'pdf url',
        'page count', 'Tags + Key Value Pairs']
        metadata_list = [] # list o lists containing metadata for each document

        # retrieve information from each document.
        if self.documents:
            length = len(self.documents)
            for i, doc_id in enumerate(self.documents):
                self.set_progress(100 * i // length)
                doc = self.client.documents.get(doc_id)
                doc_metadata = [doc.id, doc.title, doc.access, doc.canonical_url,
                doc.contributor, doc.created_at, doc.description, doc.full_text_url,
                doc.pdf_url, doc.page_count, doc.data]
                metadata_list.append(doc_metadata)
        elif self.query:
            documents = self.client.documents.search(self.query)
            length = len(documents)
            for i, doc in enumerate(documents):
                self.set_progress(100 * i // length)
                doc_metadata = [doc.id, doc.title, doc.access, doc.asset_url,
                doc.contributor, doc.created_at, doc.description, doc.full_text_url,
                doc.pdf_url, doc.page_count, doc.data]
                metadata_list.append(doc_metadata)

        # using the length variable to try and avoid overwriting files if possible.
        # potentially revisit this to ensure we arent overwriting locally. 
        with open("document_metadata"+str(length)+".csv", "w+") as file_:
            writer = csv.writer(file_)
            writer.writerow(header)

            for row in metadata_list:
                writer.writerow(row)
            
            self.upload_file(file_)

        self.set_message("Metadata scraping end!")
        # self.send_mail("Hello World!", "We finished!")


if __name__ == "__main__":
    MetadaScrape().main()
