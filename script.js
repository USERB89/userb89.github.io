const letters = [
  { char: 'ا', name: 'alif', sound: 'a', forms: ['ا', ' ', 'ـا'] },
  { char: 'ب', name: 'ba', sound: 'b', forms: ['بـ', 'ـبـ', 'ـب'] },
  { char: 'ت', name: 'ta', sound: 't', forms: ['تـ', 'ـتـ', 'ـت'] },
  { char: 'ث', name: 'tha', sound: 'th', forms: ['ثـ', 'ـثـ', 'ـث'] },
  { char: 'ج', name: 'jiim', sound: 'j', forms: ['جـ', 'ـجـ', 'ـج'] },
  { char: 'ح', name: 'hha', sound: 'h', forms: ['حـ', 'ـحـ', 'ـح'] },
  { char: 'خ', name: 'kha', sound: 'kh', forms: ['خـ', 'ـخـ', 'ـخ'] },
  { char: 'د', name: 'daal', sound: 'd', forms: ['د', ' ', 'ـد'] },
  { char: 'ذ', name: 'thaal', sound: 'dh', forms: ['ذ', ' ', 'ـذ'] },
  { char: 'ر', name: 'raa', sound: 'r', forms: ['ر', ' ', 'ـر'] },
  { char: 'ز', name: 'zay', sound: 'z', forms: ['ز', ' ', 'ـز'] },
  { char: 'س', name: 'siin', sound: 's', forms: ['سـ', 'ـسـ', 'ـس'] },
  { char: 'ش', name: 'sheen', sound: 'sh', forms: ['شـ', 'ـشـ', 'ـش'] },
  { char: 'ص', name: 'saad', sound: 's_', forms: ['صـ', 'ـصـ', 'ـص'] },
  { char: 'ض', name: 'daad', sound: 'd_', forms: ['ضـ', 'ـضـ', 'ـض'] },
  { char: 'ط', name: 'taa', sound: 't_', forms: ['طـ', 'ـطـ', 'ـط'] },
  { char: 'ظ', name: 'thaa', sound: 'dh_', forms: ['ظـ', 'ـظـ', 'ـظ'] },
  { char: 'ع', name: 'ain', sound: 'aa', forms: ['عـ', 'ـعـ', 'ـع'] },
  { char: 'غ', name: 'ghain', sound: 'gh', forms: ['غـ', 'ـغـ', 'ـغ'] },
  { char: 'ف', name: 'faa', sound: 'f', forms: ['فـ', 'ـفـ', 'ـف'] },
  { char: 'ق', name: 'qaaf', sound: 'q', forms: ['قـ', 'ـقـ', 'ـق'] },
  { char: 'ك', name: 'kaaf', sound: 'k', forms: ['كـ', 'ـكـ', 'ـك'] },
  { char: 'ل', name: 'laam', nameSound: 'l', forms: ['لـ', 'ـلـ', 'ـل'] },
  { char: 'م', name: 'meem', sound: 'm', forms: ['مـ', 'ـمـ', 'ـم'] },
  { char: 'ن', name: 'noon', sound: 'n', forms: ['نـ', 'ـنـ', 'ـن'] },
  { char: 'ه', name: 'haa2', sound: 'h2', forms: ['هـ', 'ـهـ', 'ـه'] },
  { char: 'و', name: 'waw', sound: 'w', forms: ['و', 'و', 'ـو'] },
  { char: 'ي', name: 'yaa', sound: 'y', forms: ['يـ', 'ـيـ', 'ـي'] }
];

const container = document.getElementById('lettersContainer');

letters.forEach(letter => {
    const col = document.createElement('div');
    col.className = 'col-6 col-sm-4 col-md-3 col-lg-2';

    const card = document.createElement('div');
    card.className = 'letter-card';

    const main = document.createElement('div');
    main.className = 'main-letter';
    main.textContent = letter.char;

    /* --- мини формы --- */
    const forms = document.createElement('div');
    forms.className = 'small-forms';

    letter.forms.forEach(form => {
        const span = document.createElement('span');
        span.textContent = form;

        span.addEventListener('click', (e) => {
            e.stopPropagation(); // чтобы не запускалось название
            const audio = new Audio(`audio/sounds/${letter.sound}.mp3`);
            audio.play();
        });

        forms.appendChild(span);
    });

    /* --- клик по большой букве — название буквы --- */
    card.addEventListener('click', () => {
        const audio = new Audio(`audio/names/${letter.name}.mp3`);
        audio.play();
    });

    card.appendChild(main);
    card.appendChild(forms);

    col.appendChild(card);
    container.appendChild(col);
});

