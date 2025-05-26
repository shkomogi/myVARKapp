from flask import Flask, render_template, request, session, redirect, url_for
import os

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'your_fallback_secret_key')

# VARK Questionnaire Logic (from previous code)
class VARK:

    def __init__(self):
        pass

    VARKoptions = {
        1: ["a. go with her", "b. tell her the directions", "c. write down the directions.", "d. draw, or give her a map"],
        2: ["a. see the words in your mind and choose by the way they look", "b. think about how each word sounds and choose one", "c. find it in a dictionary", "d. write both words on paper and choose one"],
        3: ["a. describe some of the highlights", "b. use a map or website to show them the places", "c. give them a copy of the printed itinerary", "d. phone, text or email"],
        4: ["a. cook something you know without the need for instructions", "b. ask friends for suggestions", "c. look through the cookbook for ideas from the pictures", "d. use a cookbook where you know there is a good recipe"],
        5: ["a. talk about, or arrange a talk for them about parks or nature reserves", "b. show them internet pictures, photographs or picture books", "c. take them to a park or nature reserve and walk with them", "d. give them a book or pamphlets about the parks or nature reserves."],
        6: ["a. Trying or testing it", "b. Reading the details about its features", "c. It is a modern design and looks good", "d. The salesperson telling me about its features"],
        7: ["a. watching a demonstration", "b. listening to somebody explaining it and asking questions", "c. diagrams and charts - visual clues", "d. written instructions – e.g. a manual or"],
        8: ["a. gave you a web address or something to read about it", "b. used a plastic model of a knee to show what was", "c. described what was wrong", "d. showed you a diagram of what was"],
        9: ["a. read the written instructions that came with the program", "b. talk with people who know about the program", "c. use the controls or keyboard", "d. follow the diagrams in the book that came with it."],
        10: ["a. things I can click on, shift or try", "b. interesting design and visual features", "c. interesting written descriptions, lists and", "d. audio channels where I can hear music, radio programs or"],
        11: ["a. The way it looks is appealing", "b. Quickly reading parts of it.", "c. A friend talks about it and recommends it.", "d. It has real-life stories, experiences and examples"],
        12: ["a. a chance to ask questions and talk about the camera and its features.", "b. clear written instructions with lists and bullet points about what to do.",
        "c. diagrams showing the camera and what each part does", "d. many examples of good and poor photos and how to improve them"],
        13: ["a. demonstrations, models or practical sessions", "b. question and answer, talk, group discussion, or guest speakers", "c. handouts, books, or readings", "d. diagrams, charts or graphs"],
        14: ["a. using examples from what you have done", "b. using a written description of your results", "c. from somebody who talks it through with", "d. using graphs showing what you had achieved"],
        15: ["a. choose something that you have had there before", "b. listen to the waiter or ask friends to recommend choices", "c. choose from the descriptions in the menu", "d. look at what others are eating or look at pictures of each dish"],
        16: ["a. make diagrams or get graphs to help explain things", "b. write a few key words and practice saying your speech over and over",
        "c. write out your speech and learn from reading it over several times", "d. gather many examples and stories to make the talk real and practical"]
    }

    VARKQstn = {
        1: "1. You are helping someone who wants to go to your airport, town centre or railway station. You would:",
        2: "2. You are not sure whether a word should be spelled `dependent' or `dependant'. You would:",
        3: "3. You are planning a holiday for a group. You want some feedback from them about the plan. You would:",
        4: "4. You are going to cook something as a special treat for your family. You would:",
        5: "5. A group of tourists want to learn about the parks or nature reserves in your area. You would:",
        6: "6. You are about to purchase a digital camera or mobile phone. Other than price, what would most influence your decision?",
        7: "7. Remember a time when you learned how to do something new. Try to avoid choosing a physical skill, e.g. riding a bike. You learned best by:",
        8: "8. You have a problem with your knee. You would prefer that the doctor:",
        9: "9. You want to learn a new program, skill or game on a computer. You would:",
        10: "10. I like websites that have:",
        11: "11. Other than price, what would most influence your decision to buy a new non-fiction book?",
        12: "12. You are using a book, DVD or website to learn how to take photos with your new digital camera. You would like to have:",
        13: "13. Do you prefer a trainer or a presenter who uses:",
        14: "14. You have finished a competition or test and would like some feedback. You would like to have feedback:",
        15: "15. You are going to choose food at a restaurant or cafe. You would:",
        16: "16. You have to make an important speech at a conference or special occasion. You would:"
    }

    # VARKletters mapping options to learning styles for each question
    VARKletters = {
        1: ['K', 'R', 'V', 'A'],
        2: ['V', 'A', 'R', 'K'],
        3: ['A', 'V', 'R', 'K'],
        4: ['K', 'A', 'V', 'R'],
        5: ['A', 'V', 'K', 'R'],
        6: ['K', 'R', 'V', 'A'],
        7: ['K', 'A', 'V', 'R'],
        8: ['R', 'K', 'A', 'V'],
        9: ['R', 'A', 'K', 'V'],
        10: ['K', 'V', 'R', 'A'],
        11: ['V', 'R', 'A', 'K'],
        12: ['A', 'R', 'V', 'K'],
        13: ['K', 'A', 'R', 'V'],
        14: ['K', 'R', 'A', 'V'],
        15: ['R', 'A', 'V', 'K'],
        16: ['V', 'A', 'R', 'K']
    }

# Instantiate the VARK class
vark_quiz = VARK()
QUESTION_IDS = sorted(vark_quiz.VARKQstn.keys())
TOTAL_QUESTIONS = len(QUESTION_IDS)

@app.route('/')
def index():
    session.clear() # Clear any previous session data
    session['answers'] = {} # Initialize answers dictionary
    return render_template('index.html')

@app.route('/question/<int:question_id>', methods=['GET', 'POST'])
def question(question_id):
    if question_id > TOTAL_QUESTIONS:
        return redirect(url_for('results'))

    question_text = vark_quiz.VARKQstn.get(question_id)
    options = vark_quiz.VARKoptions.get(question_id)

    if not question_text or not options:
        # Handle invalid question_id gracefully
        return "Question not found", 404

    if request.method == 'POST':
        selected_options = request.form.getlist('option') # getlist for multiple selections
        
        if not selected_options:
            # If no option is selected, re-render the current question with an error message
            error_message = "Please select at least one option."
            return render_template('question.html',
                                   question_id=question_id,
                                   question_text=question_text,
                                   options=options,
                                   current_question_num=question_id,
                                   total_questions=TOTAL_QUESTIONS,
                                   error=error_message)

        # Store question_id as a string in the session
        session['answers'][str(question_id)] = selected_options
        session.modified = True # Mark session as modified
        
        next_question_id = question_id + 1
        if next_question_id <= TOTAL_QUESTIONS:
            return redirect(url_for('question', question_id=next_question_id))
        else:
            return redirect(url_for('results'))

    # GET request: display the question
    return render_template('question.html',
                           question_id=question_id,
                           question_text=question_text,
                           options=options,
                           current_question_num=question_id,
                           total_questions=TOTAL_QUESTIONS)

@app.route('/results')
def results():
    user_answers = session.get('answers', {})
    vark_counts = {'V': 0, 'A': 0, 'R': 0, 'K': 0}

    # Iterate through user_answers, converting string keys back to integers
    for q_num_str, choices in user_answers.items():
        try:
            q_num = int(q_num_str) # Convert the string key back to an integer
        except ValueError:
            # Handle cases where a key might not be a valid integer if unexpected data gets into the session
            continue 
            
        for choice_char in choices:
            # Assuming 'a' is index 0, 'b' is 1, etc.
            choice_index = ord(choice_char) - ord('a')
            
            if q_num in vark_quiz.VARKletters and 0 <= choice_index < len(vark_quiz.VARKletters[q_num]):
                vark_letter = vark_quiz.VARKletters[q_num][choice_index]
                vark_counts[vark_letter] += 1

    max_count = 0
    if vark_counts:
        max_count = max(vark_counts.values())

    highest_styles = []
    for style, count in vark_counts.items():
        if count == max_count and count > 0: # Only include if it's the max AND greater than 0
            highest_styles.append(style)

    # Convert single letter codes to full names for display
    style_names = {
        'V': 'Visual',
        'A': 'Auditory',
        'R': 'Read/Write',
        'K': 'Kinesthetic'
    }
    
    # Map the highest_styles list to their full names
    result_styles_full_names = []
    # Sort for consistent output (e.g., A, K, R, V)
    highest_styles.sort() 
    for style_code in highest_styles:
        result_styles_full_names.append(style_names.get(style_code, style_code))

    return render_template('results.html',
                           vark_counts=vark_counts,
                           highest_styles=result_styles_full_names)

if __name__ == '__main__':
    app.run() # debug=True allows for auto-reloading and better error messages during development

#pip freeze > requirements.txt (python libs app depends on)