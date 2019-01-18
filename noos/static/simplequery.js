export default class SimpleQ {
	constructor(inputID, buttonID, resultsID) {
	    this.input = document.getElementById(inputID);
		this.button = document.getElementById(buttonID);
		this.resultsID = resultsID;

		this.button.onclick = (ev) => {
			d3.json("/testquery", {'method': "POST", 'body':JSON.stringify({'query':this.input.value})}).then( data => {
				var items = d3.select("#" + resultsID)
					.selectAll("div")
					.data(data)
					.text(prop => prop.content)
				items.enter()
					.append("div")
					.attr("class", "ui item")
					.text(prop => prop.content)
				items.exit().remove()
			})
		}
	}
}
