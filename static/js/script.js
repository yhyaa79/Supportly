import * as webSupporter from './supportWeb.js';

const fab = document.getElementById('myFab');

fab.addEventListener('click', () => {
    fab.classList.toggle('spin');
    //webSupporter.supporteruser()
    webSupporter.supporterWeb('لووی', 'https://loovi.ai/', 'llama-3.1-70b-instruct');
});
