const screens = document.querySelectorAll('.screen');
const navItems = document.querySelectorAll('.nav-item');
const capsule = document.getElementById('nav-capsule');
const chips = document.querySelectorAll('.module-chip');

function positionCapsule(element) {
    capsule.style.width = element.offsetWidth + 'px';
    capsule.style.left = element.offsetLeft + 'px';
}

window.addEventListener('load', () => {
    positionCapsule(navItems[0]);
});

window.addEventListener('resize', () => {
    const activeItem = document.querySelector('.nav-item.active');
    if (activeItem) positionCapsule(activeItem);
});

function switchTab(index, element) {
    navItems.forEach(item => item.classList.remove('active'));
    element.classList.add('active');
    positionCapsule(element);

    screens.forEach(screen => screen.classList.remove('active'));
    screens[index].classList.add('active');
}

function setTheme(color, rgb) {
    document.documentElement.style.setProperty('--accent', color);
    document.documentElement.style.setProperty('--accent-rgb', rgb);
}

function startScan() {
    const query = document.getElementById('osint-input').value.trim();
    if (!query) return;

    let currentDelay = 0;

    chips.forEach((chip, index) => {
        setTimeout(() => {
            chip.classList.add('scanning');
        }, currentDelay);

        currentDelay += 500;

        setTimeout(() => {
            chip.classList.remove('scanning');
            chip.classList.add('done');
        }, currentDelay);
    });

    setTimeout(() => {
        renderObsidianGraph(query);
    }, currentDelay + 200);
}

function renderObsidianGraph(targetValue) {
    document.getElementById('search-initial').style.display = 'none';
    const container = document.getElementById('search-results');
    container.style.display = 'block';

    const width = container.offsetWidth || window.innerWidth - 32;
    const height = container.offsetHeight || 400;

    const nodes = [
        { id: 'center', label: 'Запрос', val: targetValue, x: width / 2, y: height / 2, isCenter: true },
        { id: 'mod-vk', label: 'VKontakte', val: 'ID: 4820194', x: width * 0.22, y: height * 0.25 },
        { id: 'mod-wa', label: 'WhatsApp', val: 'Статус: Активен', x: width * 0.78, y: height * 0.25 },
        { id: 'mod-tg', label: 'Telegram', val: '@red_actor', x: width * 0.18, y: height * 0.72 },
        { id: 'mod-mg', label: 'Maigret', val: 'Найдено: 4 сайта', x: width * 0.50, y: height * 0.14 },
        { id: 'mod-sh', label: 'Sherlock', val: 'Совпадения: GitHub', x: width * 0.82, y: height * 0.70 },
        { id: 'mod-dx', label: 'Dyxless', val: 'Привязка к Mail', x: width * 0.50, y: height * 0.88 }
    ];

    const nodesContainer = document.getElementById('graph-nodes-container');
    const svgElement = document.getElementById('graph-svg-element');
    
    nodesContainer.innerHTML = '';
    svgElement.innerHTML = '';

    nodes.forEach(node => {
        const div = document.createElement('div');
        div.className = `graph-node ${node.isCenter ? 'center-node' : ''}`;
        div.style.left = node.x + 'px';
        div.style.top = node.y + 'px';
        div.innerHTML = `<span class="node-label">${node.label}</span><span class="node-val">${node.val}</span>`;
        nodesContainer.appendChild(div);

        if (!node.isCenter) {
            const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            line.setAttribute('x1', nodes[0].x);
            line.setAttribute('y1', nodes[0].y);
            line.setAttribute('x2', node.x);
            line.setAttribute('y2', node.y);
            line.setAttribute('class', 'graph-line');
            svgElement.appendChild(line);
        }
    });
}

function copyMirrorLink() {
    navigator.clipboard.writeText('https://t.me/flagon_bot?start=ref874920472');
                                  }
