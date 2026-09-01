import re
from typing import List, Dict, Any

class DocumentChunker:
    def __init__(self, max_chunk_size: int = 800, overlap: int = 150):
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap

    def chunk_markdown(self, content: str, doc_title: str, tech: str, version: str) -> List[Dict[str, Any]]:
        """
        Splits markdown & code docs intelligently by headings (#, ##, ###) and paragraph boundaries.
        """
        sections = re.split(r'\n(?=#{1,3}\s)', content)
        chunks = []

        chunk_id_counter = 1
        for section in sections:
            section_clean = section.strip()
            if not section_clean:
                continue

            # Extract section heading if present
            heading_match = re.match(r'^(#{1,3})\s+(.+)$', section_clean, re.MULTILINE)
            section_title = heading_match.group(2) if heading_match else doc_title

            # If section is small enough, keep as single chunk
            if len(section_clean) <= self.max_chunk_size:
                chunks.append({
                    "chunk_id": f"{tech.lower()}_{version}_{chunk_id_counter}",
                    "text": section_clean,
                    "title": doc_title,
                    "section": section_title,
                    "technology": tech,
                    "version": version
                })
                chunk_id_counter += 1
            else:
                # Split large section by paragraphs or double newlines with overlap
                paragraphs = section_clean.split('\n\n')
                current_chunk = ""

                for para in paragraphs:
                    if len(current_chunk) + len(para) <= self.max_chunk_size:
                        current_chunk += para + "\n\n"
                    else:
                        if current_chunk.strip():
                            chunks.append({
                                "chunk_id": f"{tech.lower()}_{version}_{chunk_id_counter}",
                                "text": current_chunk.strip(),
                                "title": doc_title,
                                "section": section_title,
                                "technology": tech,
                                "version": version
                            })
                            chunk_id_counter += 1
                        # Start new chunk with overlap
                        current_chunk = current_chunk[-self.overlap:] + para + "\n\n" if len(current_chunk) > self.overlap else para + "\n\n"

                if current_chunk.strip():
                    chunks.append({
                        "chunk_id": f"{tech.lower()}_{version}_{chunk_id_counter}",
                        "text": current_chunk.strip(),
                        "title": doc_title,
                        "section": section_title,
                        "technology": tech,
                        "version": version
                    })
                    chunk_id_counter += 1

        return chunks

doc_chunker = DocumentChunker()
