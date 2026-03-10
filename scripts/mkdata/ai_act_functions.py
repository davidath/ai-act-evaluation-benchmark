import re
import pdfplumber
import nltk
from nltk.tokenize import sent_tokenize
from tqdm import tqdm
DEFAULT_CACHE_DIR = 'data/cache'
nltk.download('punkt', download_dir=DEFAULT_CACHE_DIR)
nltk.download('punkt_tab', download_dir=DEFAULT_CACHE_DIR)
nltk.data.path.append(DEFAULT_CACHE_DIR)


def crop_page(plumbpage, top_rate, bottom_rate):
    assert_msg = "Argument should be pdfplumber.page.Page"
    assert isinstance(plumbpage, pdfplumber.page.Page), assert_msg
    width = plumbpage.width
    height = plumbpage.height

    top_margin = height * top_rate
    bottom_margin = height * bottom_rate

    cropped_page = plumbpage.crop((0, top_margin, width, bottom_margin))

    text = cropped_page.extract_text()
    return text


def ai_act_extract_docPart(pdf_path, top_rate,
                           bot_rates, page_range, page_indexes=[],
                           is_recital=False, AI_ACT_DEFAULT_TOP_RATE=0.1,
                           AI_ACT_DEFAULT_BOT_RATE=0.95):
    assert isinstance(page_range, list), "Range of pages should be a list"
    assert all(i >= 0 for i in page_range), "Can not have page below 0"
    pdf_reader = pdfplumber.open(pdf_path)
    if page_range is None:
        page_range = range(len(pdf_reader.pages))
    text = ''
    for page_num in tqdm(page_range, desc='Processing Document'):
        if page_num < len(pdf_reader.pages):
            # Simplified page separator to deal with footnotes in recitals
            if is_recital:
                page_text = crop_page(pdf_reader.pages[page_num],
                                      top_rate[page_num], bot_rates[page_num])

                text += page_text + "\n---END_OF_PAGE---\n"
            else:
                if page_num in page_indexes:
                    common_idc = page_indexes.index(page_num)
                    page_text = crop_page(pdf_reader.pages[page_num],
                                          top_rate[common_idc],
                                          bot_rates[common_idc])
                else:
                    page_text = crop_page(pdf_reader.pages[page_num],
                                          AI_ACT_DEFAULT_TOP_RATE,
                                          AI_ACT_DEFAULT_BOT_RATE)
                text += page_text
        else:
            print(f"Page {page_num} is out of range.")
    pdf_reader.close()
    return text


def ai_act_gather_recitals(text):
    # Use regex to ensure recitals start at a new line with (number)
    recitals = re.split(r"\n\s*\((\d+)\)\s*", text)

    # Reconstruct recitals
    recitals = [
        f"Recital {recitals[i]} {recitals[i + 1].strip()}"
        for i in range(1, len(recitals), 2)
    ]
    return recitals


def ai_act_parse_sequential_recitals(recitals):
    filtered_recitals = []
    expected_number = 1  # Start from Recital 1 or adjust as needed
    discard_mode = False

    for recital in recitals:
        # Check for a new page character and reset discard mode
        if recital.strip() == "---END_OF_PAGE---":  # Strict match:

            discard_mode = False  # Reset discard mode on a new page
            continue  # Move to the next recital after reset

        match = re.match(r"Recital (\d+)", recital)

        if match:
            recital_number = int(match.group(1))

            # Stop processing recitals after 179
            if recital_number > 179:
                break  # Exit the loop once we reach Recital 180 or higher

            # Remove any occurrence of "---END_OF_PAGE---" inside the text
            recital = recital.replace("---END_OF_PAGE---", "").strip()

            if discard_mode:
                # Resume checking only if we find the correct expected number
                # after a page break
                if recital_number == expected_number:
                    discard_mode = False
                    filtered_recitals.append(recital)
                    expected_number += 1
                continue  # Skip everything else until we find correct recital

            # Ensure the recital follows the expected sequence
            if recital_number == expected_number:
                filtered_recitals.append(recital)
                expected_number += 1
            elif recital_number > expected_number:
                # Only enter discard mode if there's an actual sequence break
                discard_mode = True
            else:
                # If the number is lower than expected,
                # might be a footnote, so ignore it
                continue

    return filtered_recitals


# Function to split text into articles while preserving headers
def ai_act_gather_articles(text):
    # Matches 'Article X' when:
    # - It starts at the beginning of a line (\n or \f)
    # - OR it follows a URL (handled separately)
    # - Ensures 'Article X' is followed by a capital letter (title)

    # Remove all text until the header "Article 1"
    # followed by "Subject Matter" appears.
    text = re.sub(r"^.*?(?=^Article 1\s*\nSubject matter\b)",
                  "", text, flags=re.DOTALL | re.MULTILINE)
    # Remove from a CHAPTER header until the next "Article" header
    text = re.sub(r"CHAPTER\s+[IVXLCDM]+\s*.*?(?=Article \d+)", "",
                  text, flags=re.DOTALL)
    # Remove from a SECTION header until the next "Article" header
    text = re.sub(r"SECTION\s+\d+\s*.*?(?=Article \d+)",
                  "", text, flags=re.DOTALL)

    articles = re.split(
        r"(?:\n|\f|(?:http\S+\s*))?(Article \d+)(?=\s+[A-Z])", text)

    # Reconstruct articles while keeping headers
    articles = [" ".join(articles[i:i+2]).strip()
                for i in range(1, len(articles), 2)]
    return articles


def ai_act_gather_annexes(text):
    # Matches 'Article X' when:
    # - It starts at the beginning of a line (\n or \f)
    # - OR it follows a URL (handled separately)
    # - Ensures 'Article X' is followed by a capital letter (title)
    # Remove SECTION headers
    # (lines that start with "SECTION" followed by digits)
    text = re.sub(r"^Section\s+\d+\s*\n?", "", text, flags=re.MULTILINE)

    annexes = re.split(
        r"(?:\n|\f|(?:http\S+\s*))?(ANNEX [IVXLCDM]+)(?=\s)", text)

    # Reconstruct annexes while keeping headers
    annexes = [" ".join(annexes[i:i+2]).strip()
               for i in range(1, len(annexes), 2)]
    return annexes


def ai_act_tokenize_recitals(recitals):
    tokenized_recitals = []
    labels = []
    for recital in recitals:
        # Extract recital header (must be at start of text)
        match = re.match(r"^(Recital \d+)", recital)
        if match:
            header = match.group(1)
            body = recital[len(header):].strip()  # Remove header from body

            # Preprocess text to remove standalone numbers and list markers
            # Remove numbered list markers
            cleaned_text = re.sub(r'^\d+\.\s*', '', body, flags=re.MULTILINE)
            # Replace multiple newlines with a space
            cleaned_text = re.sub(r'\n+', ' ', cleaned_text)

            # Tokenize body into sentences
            sentences = sent_tokenize(cleaned_text)

            # Attach header to valid sentences
            tokenized_recitals.extend(
                [f"{header}: {sentence}" for sentence in sentences])
            label_regex = re.search(r'\bRecital (\d+)\b', header)
            label = int(label_regex.group(1))
            labels.extend([int(label) for sentence in sentences])
        else:
            # If no header is found, clean and tokenize normally
            cleaned_text = re.sub(
                r'^\d+\.\s*', '', recital, flags=re.MULTILINE)
            cleaned_text = re.sub(r'\n+', ' ', cleaned_text)
            sentences = sent_tokenize(cleaned_text)
            tokenized_recitals.extend(sentences)

    return tokenized_recitals, labels


def ai_act_tokenize_articles(articles):
    tokenized_articles = []
    labels = []
    for article in articles:
        # Extract article header (must be at start of text)
        match = re.match(r"^(Article \d+)", article)
        if match:
            header = match.group(1)
            body = article[len(header):].strip()  # Remove header from body

            # Preprocess text to remove standalone numbers and list markers
            # Remove numbered list markers
            cleaned_text = re.sub(r'^\d+\.\s*', '', body, flags=re.MULTILINE)
            # Replace multiple newlines with a space
            cleaned_text = re.sub(r'\n+', ' ', cleaned_text)

            # Tokenize body into sentences
            sentences = nltk.sent_tokenize(cleaned_text)

            # Attach header to valid sentences
            tokenized_articles.extend(
                [f"{header}: {sentence}" for sentence in sentences])
            label_regex = re.search(r'\bArticle (\d+)\b', header)
            label = int(label_regex.group(1))
            labels.extend([int(label) for sentence in sentences])
        else:
            # If no header is found, clean and tokenize normally
            cleaned_text = re.sub(
                r'^\d+\.\s*', '', article, flags=re.MULTILINE)
            cleaned_text = re.sub(r'\n+', ' ', cleaned_text)
            sentences = nltk.sent_tokenize(cleaned_text)
            tokenized_articles.extend(sentences)
    return tokenized_articles, labels


def ai_act_tokenize_annexes(annexes):
    tokenized_annexes = []

    for annex in annexes:
        # Extract annex header (must be at start of text)

        match = re.match(r"^(ANNEX [IVXLCDM]+)", annex)
        if match:
            header = match.group(1)
            body = annex[len(header):].strip()  # Remove header from body

            # Preprocess text to remove standalone numbers and list markers
            # Remove numbered list markers
            cleaned_text = re.sub(r'^\d+\.\s*', '', body, flags=re.MULTILINE)
            # Replace multiple newlines with a space
            cleaned_text = re.sub(r'\n+', ' ', cleaned_text)

            # Tokenize body into sentences
            sentences = nltk.sent_tokenize(cleaned_text)

            valid_sentences = []
            for sentence in sentences:
                s = sentence.strip()
                # Skip sentences that are just a number (e.g., "2." or "3.")
                if re.match(r'^\d+\.?$', s):
                    continue

                valid_sentences.append(s)

            # Attach header to valid sentences
            tokenized_annexes.extend(
                [f"{header}: {sentence}" for sentence in valid_sentences])
        else:
            # If no header is found, clean and tokenize normally
            cleaned_text = re.sub(r'^\d+\.\s*', '', annex, flags=re.MULTILINE)
            cleaned_text = re.sub(r'\n+', ' ', cleaned_text)
            sentences = nltk.sent_tokenize(cleaned_text)
            tokenized_annexes.extend(sentences)

    return tokenized_annexes
