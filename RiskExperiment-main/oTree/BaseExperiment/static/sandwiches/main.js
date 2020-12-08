class Game {
    /** State of the game */
    constructor(duration) {
        this.duration = duration;
        this.order = null;
        this.assembled = [];
        this.count = 0;
    }

    resetSandwich() {
        this.assembled = [];
    }

    addComponent(name) {
        this.assembled.unshift(name);
    }

    delComponent(idx) {
        this.assembled.splice(idx, 1);
    }
}


class View {
    /** Rendering of game components */
    constructor(game, elem) {
        this.game = game;
        this.$root = elem;

        this.$menu = this.$root.find('#menu-column');
        this.$main = this.$root.find('#main-column');
        this.$assembly = this.$root.find('#assembly');
        this.$order = this.$root.find('#order');
        this.$timer = this.$root.find('#timer');
        this.$counter = this.$root.find('#counter');
        this.$recipe = this.$root.find('#recipe');
        this.$error = this.$root.find('#error');

        this.$recipe.on('change', 'select', (ev) => {
            this.showRecipe($(ev.target).val());
        });

        // converting clicks to game events
        this.$menu.on('click', '.add-btn', (ev) => {
            var ctrl = $(ev.target).parents('.input-group').find('select');
            var name = ctrl.val();
            ctrl.val("");
            this.$root.trigger('addComponent', {component: name});
        })

        this.$assembly.on('click', '.del-btn', (ev) => {
            var idx = Number($(ev.target).data('idx'));
            this.$root.trigger('delComponent', {idx: idx});
        });

        this.$main.find('#reset-btn').on('click', (ev) => {
            this.$root.trigger('resetSandwich');
        });

        this.$main.find('#submit-btn').on('click', (ev) => {
            this.$root.trigger('submitSandwich');
        });

    }

    render() {
        this.renderOrder();
        this.renderTimer();
        this.renderCounter();
        this.renderSandwich();
    }

    renderOrder() {
        this.$order.text(this.game.order);
    }

    renderTimer(time) {
        var min = Math.floor(time / 60);
        var sec = time % 60;
        this.$timer.text(min + ":" + sec);
    }

    renderCounter() {
        this.$counter.text(this.game.count);
    }

    renderSandwich() {
        var sandwich = this.game.assembled;
        this.$assembly.empty()
        this.$assembly.append(sandwich.map((name, idx) => `
            <li style="background-image: url(${js_vars.images[name]})">
                <span class="badge badge-light">${name}</span>
                <button type="button" class="btn btn-sm del-btn" data-idx="${idx}">❌</button>
            </li>`));

        this.$main.find('#submit-btn').prop('disabled', sandwich.length == 0);
    }

    showRecipe(name) {
        var recipe = js_vars.menu[name];
        var $recipe = this.$recipe.find('ul');
        $recipe.empty();
        $recipe.append(recipe.map((item) => `<li>${item}</li>`));
    }

    hideRecipe() {
        this.$recipe.find('select').val("");
        this.$recipe.find('ul').empty();
    }

    showError(message) {
        this.$error.modal('show').find('.modal-body').text(message);
    }

    hideError() {
        this.$error.modal('hide');
    }
}


class Controller {
    /** Main logic of communication with user and server */
    constructor(game, view) {
        this.game = game;
        this.view = view;
        this.timeout = this.game.duration;

        // handling received messages
        // recieved can be single message or am array of messages
        window.liveRecv = (message) => {
            var msgs = $.isArray(message) ? message : [message];
            for(var msg of msgs) {
                if (msg.type == 'status') {
                    this.recvStatus(msg);
                } else if (msg.type == 'order') {
                    this.recvOrder(msg);
                } else if(msg.type == 'error') {
                    this.recvError(msg);
                } else {
                    console.error("Unrecognized message:", msg);
                }
            }
        }

        // handling events from view
        this.view.$root.on('addComponent', (ev, data) => this.addComponent(data.component));
        this.view.$root.on('delComponent', (ev, data) => this.delComponent(data.idx));
        this.view.$root.on('resetSandwich', (ev) => this.resetSandwich());
        this.view.$root.on('submitSandwich', (ev) => this.submitSandwich());
    }

    recvStatus(msg) {
        // received status message
        this.game.count = msg.performed;
        this.view.renderCounter();
    }

    recvOrder(msg) {
        // received new order
        this.game.order = msg.order;
        this.view.renderOrder();
        this.game.resetSandwich();
        this.view.renderSandwich();
        this.view.hideRecipe();
    }

    recvError(msg) {
        // received error after submitting sandwich
        this.view.showError(`${msg.mismatches} ingredients mismatched`);
    }

    sendStart() {
        // sending start game request
        window.liveSend({type: 'start'});
    }

    sendSendwich() {
        // submitting sandwich
        window.liveSend({'type': 'sandwich', 'components': this.game.assembled});
    }

    addComponent(item) {
        // user adding a new component
        this.game.addComponent(item);
        this.view.renderSandwich();
    }

    delComponent(idx) {
        // user removing a component
        this.game.delComponent(idx);
        this.view.renderSandwich();
    }

    resetSandwich() {
        // user resetting the sandwich
        this.game.resetSandwich();
        this.view.renderSandwich();
    }

    submitSandwich() {
        // user submitting sandwich
        this.sendSendwich();
    }

    start() {
        this.view.render();

        // requesting server to send first order
        this.sendStart();

        // starting timer
        this.view.renderTimer(this.timeout);
        window.setInterval(() => {
            this.timeout -= 1;
            this.view.renderTimer(this.timeout);
            if (this.timeout <= 0) this.finish();
        }, 1000);
    }

    finish() {
        // completing game - submit whole page form
        $("#form").submit();
    }
}

var game, view, ctrl;
$(function() {
    game = new Game(js_vars['duration']);
    view = new View(game, $('body'));
    ctrl = new Controller(game, view);
    $("#finish").hide();
    ctrl.start();
})

function complete() {
    game.assembled = js_vars.menu[game.order].slice();
    view.renderSandwich();
}