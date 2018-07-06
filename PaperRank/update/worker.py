from ..util import Database
from .citation.ncbi_citation import NCBICitation as Citation
import logging


class Worker:
    def __init__(self, db: Database, citation: Citation):
        self.db = db
        self.citation = citation

        if self.citation.error:
            # Escape if there is an error
            return

        # Adding to `SEEN` and `INSTANCE`
        self.db.addMultiple(database='S', data=[self.citation.id])
        self.db.addMultiple(database='I', data=[self.citation.id])

        # Building inbound and outbound tuples
        out_tuples = ['("{0}","{1}")'.format(self.citation.id, i)
                      for i in self.citation.outbound]
        in_tuples = ['("{0}","{1}")'.format(i, self.citation.id)
                     for i in self.citation.inbound]

        if len(out_tuples) + len(in_tuples) > 0:
            # Check if inbound or outbound citations exist

            # Adding tuples to `GRAPH`
            self.db.addMultiple(database='G', data=[*in_tuples, *out_tuples])

            # Save outbound citations to `OUT`
            self.db.addMultiple(database='O',
                                data={
                                    self.citation.id: self.citation.outbound
                                })

            # TODO: Add inbound and outbound citations to the EXPLORE
            # Figure out how to do this without multiple database calls,
            # currently you would need one for each pubmedID
            # Why? To check `SEEN`, and then to add to `EXPLORE`
        else:
            # No inbound or outbound citations; add to `DANGLING`
            self.db.addMultiple(database='D', data=[self.citation.id])

        # Remove current ID from `INSTANCE`
        self.db.removeMultiple(database='I', data=[self.citation.id])
