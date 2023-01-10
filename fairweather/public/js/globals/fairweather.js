// Copyright (c) 2023, Yefri Tavarez and contributors
// For license information, please see license.txt
// es-lint: disable

frappe.dedent = function (strings, ...values) {
	let result = '';

	// Concatenate all of the strings and place them in an array.
	let stringArray = strings.concat(values);

	// Find the minimum common indentation level.
	let minIndent = Number.MAX_VALUE;
	for (let i = 0; i < stringArray.length; i++) {
		let lines = stringArray[i].split('\n');
		for (let j = 0; j < lines.length; j++) {
			let indent = lines[j].search(/\S/);
			if (indent !== -1 && indent < minIndent) {
				minIndent = indent;
			}
		}
	}

	// Remove the common indentation from each line.
	for (let i = 0; i < stringArray.length; i++) {
		let lines = stringArray[i].split('\n');
		for (let j = 0; j < lines.length; j++) {
			lines[j] = lines[j].slice(minIndent);
		}
		result += lines.join('\n');
	}

	return result;
};
