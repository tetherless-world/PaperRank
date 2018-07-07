from ..util import Database
from .citation.ncbi_citation import NCBICitation as Citation
import logging


class Worker:
    def __init__(self, db: Database, citation: Citation):
        """Worker class initialization. Adds tuples to GRAPH, maps outbound
        citations in OUT, adds unseen IDs to EXPLORE, and adds and removes
        current ID to and from INSTANCE.
        
        Arguments:
            db {Database} -- Database to be used for data transactions.
            citation {Citation} -- Citation object to be parsed.
        """

        self.db = db
        self.citation = citation

        if self.citation.error:
            # Escape if there is an error
            return

        # Adding to `SEEN`
        self.db.addMultiple(database='S', data=[self.citation.id])

        # Building inbound and outbound tuples
        out_tuples = ['("{0}","{1}")'.format(self.citation.id, i)
                      for i in self.citation.outbound]
        in_tuples = ['("{0}","{1}")'.format(i, self.citation.id)
                     for i in self.citation.inbound]

        if (len(out_tuples) + len(in_tuples)) > 0:
            # Check if inbound or outbound citations exist

            # Adding tuples to `GRAPH`
            self.db.addMultiple(database='G', data=[*in_tuples, *out_tuples])

            # Save outbound citations to `OUT`
            self.db.addMultiple(database='O',
                                data={
                                    self.citation.id: self.citation.outbound
                                })

            # Utilizing redis base class pipeline to execute commands in order
            # see: https://bit.ly/2u0J96d

            # Create pipeline object
            pipe = self.db.r.pipeline()
            # Add all inbound and outbound IDs to EXPLORE
            pipe.sadd('EXPLORE',
                      *self.citation.inbound, *self.citation.outbound)
            # Store the difference of `EXPLORE`` and `SEEN` in `EXPLORE`
            pipe.sdiffstore('EXPLORE', 'EXPLORE', 'SEEN')
            # Execute commands
            pipe.execute()

        else:
            # No inbound or outbound citations; add to `DANGLING`
            self.db.addMultiple(database='D', data=[self.citation.id])

        # Remove current ID from `INSTANCE`
        self.db.removeMultiple(database='I', data=[self.citation.id])
