export default class NewPropositionPage {
    constructor(causeID, contentID, submitID) {
        this.causeEl = document.getElementById(causeID)
        this.contentEl = document.getElementById(contentID)
        this.compareEL = document.getElementById(submitID)
        this.resultsEL = document.getElementById("results")
        this.submitEL = document.getElementById("submit_btn")

        this.compareEL.onclick = ev => this.query_sims(ev, this)
        this.submitEL.onclick = ev => this.submit(ev, this)


    }

    query_sims(ev)  {
            this.resultsEL.style.visibility = "visible";
            const q = this.contentEl.value ;
            if(q == "") return ;
            d3.json("/search_propositions", {'method': "POST", 'body':JSON.stringify({'query':q, 'limit':30})}).then(propositions => {
                var items = d3.select("#props_similaires")
                    .selectAll("div.prop")
                    .data(propositions)
                    .html(this.buildHTML)
                items.enter()
                    .append("div")
                    .attr("class", "prop ui item")
                    .html(this.buildHTML)
                items.exit().remove()
            })
        return false; // don't submit the form
        }

    submit(ev) {
        document.getElementById("form").submit()
    }


    buildHTML(prop) {
        return `en colère contre <strong>${prop.cause}</strong> je propose de <strong>${prop.content}</strong>`
    }


}