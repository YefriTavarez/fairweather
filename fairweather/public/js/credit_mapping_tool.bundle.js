frappe.provide("fairweather");
function setup(frm) {
	console.log("Hello from bundle.js");
	this.frm = frm;
}

function customer(frm) {
	const { doc } = frm;
	console.log(`customer -> ${doc.customer}`);
}

console.log("Hello from bundle.js");

fairweather.creditController = {
	setup,
	customer,
}