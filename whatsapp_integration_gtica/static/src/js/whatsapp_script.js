/** @odoo-module */

import { patch } from "@web/core/utils/patch";
import { browser } from "@web/core/browser/browser";

window.open = function (open) {
    return function (url, name, features) {
        name = name || "default_window_name"
        let ws = 'web.whatsapp.com'
        let wm = 'wa.me';
        let p_one = url.indexOf(ws);
        let p_two = url.indexOf(wm);
        if ((p_one !== -1) || (p_two !== -1))
            name = 'window_whatasapp'

        return open.call(window, url, name, features);
    };
}(window.open);

patch(browser, "send_whatsapp", {
    open: window.open.bind(window)
});
