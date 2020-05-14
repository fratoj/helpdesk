const helpSocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/help/'
);

helpSocket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    if (document.querySelector('#question') === null) {
        let question_div = document.createElement("DIV");
        question_div.setAttribute('id', 'question');
        question_div.setAttribute('style', 'border-bottom: double;');
        question_div.textContent = 'You asked: ' + data.question + '. Did you mean:';
        document.querySelector('#help-log').appendChild(question_div);
    }
    let category_div = document.createElement("DIV");
    category_div.textContent = data.category;
    document.querySelector('#help-log').appendChild(category_div);
    let answer_div = document.createElement("DIV");
    answer_div.textContent = data.message;
    if (data.fuzz_ratio === 100) {
        answer_div.setAttribute('style', 'padding-left: 4px;color: red;');
    } else {
        answer_div.setAttribute('style', 'padding-left: 4px;');
    }
    document.querySelector('#help-log').appendChild(answer_div);
};

helpSocket.onclose = function(e) {
    console.error('Chat socket closed unexpectedly');
};

document.querySelector('#question-input').focus();
document.querySelector('#question-input').onkeyup = function(e) {
    if (e.keyCode === 13) {  // enter, return
        document.querySelector('#question-submit').click();
    }
};

document.querySelector('#question-submit').onclick = function(e) {
    const questionInputDom = document.querySelector('#question-input');
    let question = questionInputDom.value;
    if (question.slice(-1) === '?' || question.slice(-1) === '.') {
        question = question.slice(0, -1);
    }
    helpSocket.send(JSON.stringify({
        'question': question
    }));
    questionInputDom.value = '';
    document.querySelector('#help-log').innerHTML = "";
};
