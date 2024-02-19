var button = document.querySelectorAll(".add-word");
let state = 0;
// Creating a form
for (let i = 0; i < 3; i++) {
    button[i].addEventListener('click', function() {
        let row1 = document.querySelector('.form-popup');
        let form = document.createElement("form");  
        form.setAttribute("method", "post")
        form.setAttribute("autocomplete", "off")
        form.setAttribute("action", "/add_words")
        row1.style.borderRadius = "25px"
        form.style.borderRadius = "25px"
        form.classList.add("form-container")

        let word = document.createElement("input");
        word.setAttribute("placeholder", "word")
        word.setAttribute("name", "AddWord");
        word.classList.add("form-element")

        let meaning = document.createElement("input");
        meaning.setAttribute("placeholder", "meaning");
        meaning.setAttribute("name", "meaning");
        meaning.classList.add("form-element")

        let collumn = document.createElement("input");
        collumn.setAttribute("type", "hidden")
        collumn.setAttribute("name", "collumn")

        if (button[i].id == "WordsWillLearn") {

            collumn.setAttribute("value", "WordsWillLearn")
            row1.style.backgroundColor = "#8297E9"
            form.style.backgroundColor = "#8297E9"
        }

        else if (button[i].id == "LearningWords") {
            collumn.setAttribute("value", "LearningWords")
            row1.style.backgroundColor = "#ffbb7a"
            form.style.backgroundColor = "#ffbb7a"  
        }

        else {
            collumn.setAttribute("value", "MasteredWords")
            row1.style.backgroundColor = "#8EFF90"
            form.style.backgroundColor = "#8EFF90"  
        }
        

        let example = document.createElement("input");
        example.setAttribute("placeholder", "example");
        example.setAttribute("name", "example");
        example.classList.add("form-element")

        let submit = document.createElement("button")
        submit.setAttribute("type", "submit")
        submit.style.borderRadius = "25px"
        submit.style.border = "none"
        submit.style.transition = "0.3s"

        if (button[i].id == "WordsWillLearn") {
            submit.style.backgroundColor = "#8297E9";
            submit.addEventListener('mouseover', function() {
                submit.style.backgroundColor = "#41549e"
            })
            submit.addEventListener('mouseout', function() {
                submit.style.backgroundColor = "#8297E9"
            })
        }

        else if (button[i].id == "LearningWords") {
            submit.style.backgroundColor = "#ffbb7a";
            submit.addEventListener('mouseover', function() {
                submit.style.backgroundColor = "#e8a566"
            })
            submit.addEventListener('mouseout', function() {
                submit.style.backgroundColor = "#ffbb7a"
            })
        }
        
        else {
            submit.style.backgroundColor = "#8EFF90";
            submit.addEventListener('mouseover', function() {
                submit.style.backgroundColor = "#57a058"
            })
            submit.addEventListener('mouseout', function() {
                submit.style.backgroundColor = "#8EFF90"
            })
        }
        submit.innerHTML = "Add word"

        let br1 = document.createElement("br");
        let br = document.createElement("br");
        let br2 = document.createElement("br");
        let br3 = document.createElement("br");

        if (state == 0){

            form.appendChild(word);
            form.appendChild(br);

            form.appendChild(meaning);
            form.appendChild(br1);

            form.appendChild(example);
            form.appendChild(br2);
            
            form.appendChild(collumn);
            form.appendChild(br3)

            form.appendChild(submit)

            row1.appendChild(form);
            row1.style.display = "block"

            state = 1;
        }

        else if (state == 1) {
            // Remove the form element
            let formToRemove = row1.querySelector('.form-container');
            if (formToRemove) {
                row1.removeChild(formToRemove);
            }
        
            row1.style.display = "none";
            state = 0;
        }
    })
}

a = document.getElementsByTagName("strong")
let len = a.length;

for ( let i = 0; i < len; i++) {
    let toggle = document.getElementById(i);
    let hiddenContent = document.getElementsByClassName(i)[0]
    toggle.addEventListener("click", function() {
        if (hiddenContent.style.display == "none") {
            hiddenContent.style.display = "block";
        }
        else {
            hiddenContent.style.display = "none";
        }
    })
}

meanings = document.getElementsByClassName('meaning');
for (let i = 0; i < meanings.length; i++) {
    meanings[i].contentEditable = true;
    let pre_inner_html = meanings[i].innerHTML;

    meanings[i].addEventListener('blur', function() {
        let currentElement = event.target;
        let word_id = currentElement.getAttribute('data-meaning-index');
        post_inner_html = currentElement.innerHTML;
        
        if (pre_inner_html !== post_inner_html) {
            let meaning_form = document.createElement("form");
            meaning_form.setAttribute("method", "post");
            meaning_form.setAttribute("action", "/change_meaning");

            word_id_input = document.createElement("input");
            word_id_input.setAttribute("type", "hidden")
            word_id_input.setAttribute("name", "word_id")
            word_id_input.setAttribute("value", word_id);

            inner_html_input = document.createElement("input")
            inner_html_input.setAttribute("type", "hidden")
            inner_html_input.setAttribute("name", "meaning")
            inner_html_input.setAttribute("value", post_inner_html)

            meaning_form.appendChild(word_id_input);
            meaning_form.appendChild(inner_html_input);


            document.body.appendChild(meaning_form)

            meaning_form.submit();

        }
    });
}