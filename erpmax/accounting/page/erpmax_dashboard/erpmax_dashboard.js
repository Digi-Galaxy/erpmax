frappe.pages["erpmax-dashboard"].on_page_load = function (wrapper) {
    const page = frappe.ui.make_app_page({
        parent: wrapper,
        title: __("ERPMax Dashboard"),
        single_column: true,
    });

    const dash = new ERPMaxDashboard(page);
    page.set_secondary_action(__("Refresh"), () => dash.reload(), "refresh");
};

const ROOT_TYPES = ["Asset", "Liability", "Equity", "Income", "Expense"];
const ALL_BOXES = [...ROOT_TYPES, "NetProfit"];
const DEBIT_NORMAL = new Set(["Asset", "Expense"]);
const ANIM_MS = 450;
const FLASH_MS = 2000;

const VOUCHER_SUMMARY = {
    "Sales Invoice": __("A sale recorded revenue and a receivable."),
    "Purchase Invoice": __("A purchase recorded a cost and a payable."),
    "Payment Entry": __("A payment moved funds between accounts."),
    "Journal Entry": __("A manual journal entry adjusted accounts directly."),
};

function line_delta(root_type, debit, credit) {
    const d = flt(debit);
    const c = flt(credit);
    return DEBIT_NORMAL.has(root_type) ? d - c : c - d;
}

class ERPMaxDashboard {
    constructor(page) {
        this.page = page;
        this.company = frappe.defaults.get_default("company");
        this.currency = frappe.boot.sysdefaults.currency;
        this.scope = "fy";
        this.date_range = { start: null, end: null };
        this.boxes = { Asset: 0, Liability: 0, Equity: 0, Income: 0, Expense: 0 };
        this.displayed = { ...this.boxes, NetProfit: 0 };
        this.lastImpact = {};
        this._seq = 0;
        this.render_skeleton();
        this.setup_controls();
        this.bind_realtime();
        this.init_company().then(() => {
            this.refresh();
            this.load_feed();
        });
    }

    async init_company() {
        if (!this.company) {
            try {
                const rows = await frappe.db.get_list("Company", { fields: ["name"], order_by: "creation asc", limit: 1 });
                if (rows && rows.length) this.company = rows[0].name;
            } catch (e) {}
        }
        if (this.company) this.company_field.set_value(this.company);
    }

    render_skeleton() {
        const box = (root, label, kind) => `
            <div class="db-box ${kind} db-clickable" data-root="${root}" role="button" tabindex="0">
                <div class="db-box-hint">${__("View accounts")} →</div>
                <div class="db-box-label">${label}</div>
                <div class="db-box-value"><span class="db-num" data-num="${root}">—</span></div>
                <div class="db-box-impact" data-impact="${root}"></div>
            </div>`;

        const eqterm = (root, label) =>
            `<span class="db-eq-t"><span class="db-eq-lbl">${label}</span> <span class="db-num" data-num="${root}">—</span></span>`;

        $(`
            <style>
                .db-wrap { max-width: 1100px; margin: 0 auto; }
                .db-equation { border: 1px solid var(--border-color); border-radius: 14px; padding: 22px 26px 20px; margin: 14px 0 6px; background: var(--card-bg, var(--fg-color)); }
                .db-eq-kicker { font-size: 11px; letter-spacing: 0.14em; text-transform: uppercase; font-weight: 700; color: var(--primary); margin-bottom: 12px; }
                .db-eq-main { display: flex; flex-wrap: wrap; align-items: baseline; gap: 8px 12px; font-size: 19px; }
                .db-eq-t { display: inline-flex; align-items: baseline; gap: 7px; }
                .db-eq-lbl { color: var(--text-muted); }
                .db-eq-main .db-num { font-weight: 700; color: var(--text-color); font-variant-numeric: tabular-nums; }
                .db-eq-op { color: var(--text-muted); font-weight: 600; }
                .db-eq-status { margin-left: auto; font-weight: 700; font-size: 12.5px; padding: 4px 12px; border-radius: 999px; }
                .db-eq-status.ok { color: #16a34a; background: rgba(34, 197, 94, 0.16); }
                .db-eq-status.warn { color: #dc2626; background: rgba(239, 68, 68, 0.16); }
                .db-section { margin-top: 22px; }
                .db-section-head { display: flex; align-items: center; gap: 9px; margin: 0 2px 10px; }
                .db-section-dot { width: 8px; height: 8px; border-radius: 2px; background: var(--primary); }
                .db-section-title { font-size: var(--text-sm); font-weight: 600; letter-spacing: 0.06em; text-transform: uppercase; color: var(--text-muted); }
                .db-section-body { display: flex; gap: 12px; flex-wrap: wrap; border: 1px solid var(--border-color); border-radius: 12px; padding: 14px; }
                .db-box { flex: 1 1 180px; min-width: 168px; position: relative; border: 1px solid var(--border-color); border-radius: 10px; padding: 16px 18px 14px; background: var(--card-bg, var(--fg-color)); cursor: pointer; transition: border-color 0.12s ease; }
                .db-box:hover { border-color: var(--primary); }
                .db-box-label { font-size: var(--text-sm); color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.04em; }
                .db-box-value { font-size: 27px; font-weight: 600; margin-top: 4px; color: var(--text-color); font-variant-numeric: tabular-nums; }
                .db-box-hint { position: absolute; top: 14px; right: 16px; font-size: 10px; font-weight: 700; text-transform: uppercase; color: var(--primary); opacity: 0; transition: opacity 0.12s ease; }
                .db-box:hover .db-box-hint { opacity: 1; }
                .db-box-impact { margin-top: 13px; min-height: 31px; }
                .db-impact-delta { font-size: var(--text-sm); font-weight: 700; }
                .db-impact-delta.up { color: #16a34a; }
                .db-impact-delta.down { color: #dc2626; }
                .db-impact-cap { font-size: 11px; color: var(--text-muted); }
                .db-box.flash-up { animation: db-flash-up 2s ease-out; }
                .db-box.flash-down { animation: db-flash-down 2s ease-out; }
                @keyframes db-flash-up { 0%, 30% { background: rgba(34, 197, 94, 0.16); } 100% { background: var(--card-bg); } }
                @keyframes db-flash-down { 0%, 30% { background: rgba(239, 68, 68, 0.16); } 100% { background: var(--card-bg); } }
                .db-toolbar { display: flex; align-items: center; margin-top: 4px; }
                .db-scope { display: inline-flex; margin-left: auto; border: 1px solid var(--border-color); border-radius: 8px; overflow: hidden; }
                .db-scope-tab { border: none; background: transparent; cursor: pointer; padding: 6px 14px; font-size: var(--text-sm); font-weight: 500; color: var(--text-muted); border-right: 1px solid var(--border-color); }
                .db-scope-tab:last-child { border-right: none; }
                .db-scope-tab.active { background: var(--primary); color: #fff; font-weight: 600; }
                .db-feed { margin-top: 26px; }
                .db-feed-head { display: flex; align-items: center; gap: 9px; margin: 0 2px 10px; }
                .db-feed-title { font-size: var(--text-sm); font-weight: 600; text-transform: uppercase; color: var(--text-muted); }
                .db-feed-list { max-height: 480px; overflow-y: auto; border: 1px solid var(--border-color); border-radius: 12px; }
                .db-feed-row { padding: 12px 16px; border-bottom: 1px solid var(--border-color); }
                .db-feed-row:last-child { border-bottom: none; }
                .db-feed-head { display: flex; align-items: center; gap: 10px; margin-bottom: 6px; }
                .db-feed-voucher { font-weight: 600; }
                .db-feed-line { display: flex; gap: 8px; align-items: baseline; font-size: var(--text-sm); padding: 1px 0; }
                .db-tag { display: inline-block; min-width: 26px; text-align: center; font-size: 11px; font-weight: 600; padding: 1px 6px; border-radius: 4px; }
                .db-tag.up { background: rgba(34, 197, 94, 0.16); color: #16a34a; }
                .db-tag.down { background: rgba(239, 68, 68, 0.16); color: #dc2626; }
                .db-feed-empty { padding: 16px; color: var(--text-muted); }
            </style>
            <div class="db-wrap">
                <div class="db-toolbar">
                    <div class="db-scope" role="tablist">
                        <button class="db-scope-tab active" data-scope="fy">${__("This Fiscal Year")}</button>
                        <button class="db-scope-tab" data-scope="all">${__("All Time")}</button>
                    </div>
                </div>
                <div class="db-equation">
                    <div class="db-eq-kicker">${__("The Accounting Equation")}</div>
                    <div class="db-eq-main">
                        ${eqterm("Asset", __("Assets"))}
                        <span class="db-eq-op">=</span>
                        ${eqterm("Liability", __("Liabilities"))}
                        <span class="db-eq-op">+</span>
                        ${eqterm("Equity", __("Equity"))}
                        <span class="db-eq-op">+</span>
                        ${eqterm("NetProfit", __("Net Profit"))}
                        <span class="db-eq-status" data-eq-status></span>
                    </div>
                </div>
                <div class="db-section bs">
                    <div class="db-section-head"><span class="db-section-dot"></span><span class="db-section-title">${__("Balance Sheet")}</span></div>
                    <div class="db-section-body">
                        ${box("Asset", __("Assets"), "bs")}
                        ${box("Liability", __("Liabilities"), "bs")}
                        ${box("Equity", __("Equity"), "bs")}
                    </div>
                </div>
                <div class="db-section pl">
                    <div class="db-section-head"><span class="db-section-dot"></span><span class="db-section-title">${__("Profit & Loss")}</span></div>
                    <div class="db-section-body">
                        ${box("Income", __("Income"), "pl")}
                        ${box("Expense", __("Expense"), "pl")}
                        ${box("NetProfit", __("Net Profit"), "pl")}
                    </div>
                </div>
                <div class="db-feed">
                    <div class="db-feed-head"><span class="db-section-dot"></span><span class="db-feed-title">${__("Recent Transactions")}</span></div>
                    <div class="db-feed-list"></div>
                </div>
            </div>
        `).appendTo(this.page.main);

        this.$feed = this.page.main.find(".db-feed-list");
    }

    setup_controls() {
        this.company_field = this.page.add_field({
            fieldname: "company", label: __("Company"), fieldtype: "Link", options: "Company",
            change: () => {
                const val = this.company_field.get_value();
                if (val && val !== this.company) { this.company = val; this.reload(); }
            },
        });
        if (this.company) this.company_field.set_value(this.company);

        this.page.main.find(".db-scope-tab").on("click", (e) => {
            const scope = e.currentTarget.getAttribute("data-scope");
            if (scope === this.scope) return;
            this.scope = scope;
            this.page.main.find(".db-scope-tab").toggleClass("active", false).filter(`[data-scope="${scope}"]`).toggleClass("active", true);
            this.reload();
        });

        this.page.main.find(".db-box.db-clickable").on("click", (e) => this.open_breakdown(e.currentTarget.getAttribute("data-root")));
    }

    open_breakdown(root) {
        if (!root || root === "NetProfit") return;
        frappe.call({
            method: "erpmax.accounting.api.dashboard.get_account_breakdown",
            args: { company: this.company, root_type: root, scope: this.scope },
            callback: (r) => {
                const rows = r.message || [];
                const d = new frappe.ui.Dialog({ size: "small" });
                d.set_title(__("{0} — account breakdown", [root]));
                d.$body.html(this.render_breakdown(rows));
                d.show();
            },
        });
    }

    render_breakdown(rows) {
        if (!rows.length) return `<div style="padding:12px;color:var(--text-muted)">${__("No account activity in this scope.")}</div>`;
        const total = rows.reduce((s, a) => s + flt(a.balance), 0);
        return rows.map(a => `
            <div style="display:flex;justify-content:space-between;padding:8px 2px;border-bottom:1px solid var(--border-color)">
                <span>${a.account}</span>
                <span style="font-weight:600">${format_currency(a.balance, this.currency)}</span>
            </div>
        `).join("") + `<div style="display:flex;justify-content:space-between;padding:10px 2px;font-weight:700;border-top:2px solid var(--border-color)"><span>Total</span><span>${format_currency(total, this.currency)}</span></div>`;
    }

    reload() { this.refresh(); this.load_feed(); }

    refresh() {
        frappe.call({
            method: "erpmax.accounting.api.dashboard.get_balances",
            args: { company: this.company, scope: this.scope },
            callback: (r) => {
                if (!r.message) return;
                this.company = r.message.company;
                this.currency = r.message.currency;
                this.date_range = r.message.date_range || { start: null, end: null };
                const b = r.message.boxes || {};
                ROOT_TYPES.forEach(rt => this.boxes[rt] = flt(b[rt]));
                this.paint_instant();
            },
        });
    }

    paint_instant() {
        this.lastImpact = {};
        const values = { ...this.boxes, NetProfit: this.boxes.Income - this.boxes.Expense };
        Object.keys(values).forEach(root => {
            this.displayed[root] = values[root];
            this.page.main.find(`[data-num="${root}"]`).text(format_currency(values[root], this.currency));
        });
        this.update_equation();
    }

    update_equation() {
        const net_profit = this.boxes.Income - this.boxes.Expense;
        const lhs = this.boxes.Asset;
        const rhs = this.boxes.Liability + this.boxes.Equity + net_profit;
        const balanced = Math.abs(lhs - rhs) < 0.005;
        this.page.main.find("[data-eq-status]").text(balanced ? "✓ " + __("Balanced") : "⚠ " + __("Off by {0}", [format_currency(lhs - rhs, this.currency)])).toggleClass("ok", balanced).toggleClass("warn", !balanced);
    }

    bind_realtime() {
        frappe.realtime.on("erpmax_gl_posted", (data) => {
            if (!data || (this.company && data.company !== this.company)) return;
            this.apply_event(data);
            this.prepend_feed_row(data);
        });
    }

    apply_event(data) {
        const deltas = { Asset: 0, Liability: 0, Equity: 0, Income: 0, Expense: 0 };
        (data.lines || []).forEach(line => {
            if (line.root_type in deltas) deltas[line.root_type] += line_delta(line.root_type, line.debit, line.credit);
        });
        ROOT_TYPES.forEach(rt => {
            if (Math.abs(deltas[rt]) < 0.005) return;
            this.boxes[rt] = this.displayed[rt] + deltas[rt];
            this.displayed[rt] = this.boxes[rt];
            this.page.main.find(`[data-num="${rt}"]`).text(format_currency(this.boxes[rt], this.currency));
            this.flash_box(rt, deltas[rt] > 0);
        });
        this.update_equation();
    }

    flash_box(root, up) {
        const el = this.page.main.find(`.db-box[data-root="${root}"]`).get(0);
        if (!el) return;
        el.classList.remove("flash-up", "flash-down");
        void el.offsetWidth;
        el.classList.add(up ? "flash-up" : "flash-down");
        setTimeout(() => el.classList.remove("flash-up", "flash-down"), FLASH_MS + 50);
    }

    load_feed() {
        frappe.call({
            method: "erpmax.accounting.api.dashboard.get_recent_vouchers",
            args: { company: this.company, limit: 15, scope: this.scope },
            callback: (r) => {
                this.$feed.empty();
                const vouchers = r.message || [];
                if (!vouchers.length) { this.$feed.append(`<div class="db-feed-empty">${__("No transactions yet.")}</div>`); return; }
                vouchers.forEach(v => this.$feed.append(this.render_feed_row(v)));
            },
        });
    }

    prepend_feed_row(voucher) {
        if (!voucher || !voucher.voucher_no) return;
        this.$feed.find(".db-feed-empty").remove();
        this.$feed.prepend($(this.render_feed_row(voucher)));
    }

    render_feed_row(voucher) {
        const url = `/app/${frappe.router.slug(voucher.voucher_type)}/${encodeURIComponent(voucher.voucher_no)}`;
        const lines = (voucher.lines || []).map(line => {
            const is_debit = flt(line.debit) > 0;
            const tag = is_debit ? "Dr" : "Cr";
            const amount = format_currency(is_debit ? line.debit : line.credit, this.currency);
            const up = line_delta(line.root_type, line.debit, line.credit) >= 0;
            return `<div class="db-feed-line"><span class="db-tag ${up ? "up" : "down"}">${tag}</span><span style="flex:1">${line.account}</span><span>${amount}</span></div>`;
        }).join("");
        return `<div class="db-feed-row"><div class="db-feed-head"><div class="db-feed-voucher"><a href="${url}">${voucher.voucher_type} ${voucher.voucher_no}</a></div></div><div>${lines}</div></div>`;
    }
}
