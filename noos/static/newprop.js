export default class NewPropositionPage {
    constructor(causeID, contentID, submitID, propURL) {
        this.causeEl = document.getElementById(causeID)
        this.contentEl = document.getElementById(contentID)
        this.compareEL = document.getElementById(submitID)
        this.resultsEL = document.getElementById("results")
        this.submitEL = document.getElementById("submit_btn")
        this.propURL = propURL;

        this.compareEL.onclick = ev => this.query_sims(ev, this)
        this.submitEL.onclick = ev => this.submit(ev, this)
        this.page = 1
        this.itemPerPage = 3

    }


    selectPage(n) {
        this.page = n
        this.query_sims(null)
    }

    build_pagination_menu(count) {
        var nbPages = Math.ceil(count / this.itemPerPage)
        nbPages = Math.min(10, nbPages)
        console.log(nbPages, "pages")
        var data = []
        for(var i = 1;i <= nbPages; i++) data.push(i) ;
        console.log(data)

        var sel = d3.select("#page_menu")
            .selectAll("a.item")
            .data(data)
            .text(d => d)
            .attr("class", d => (d == this.page) ? "active item" : "item")
            .on('click',d => {this.selectPage(d); return false})
        sel.enter()
            .append("a")
            .attr("class", d => d == this.page ? "active item" : "item")
            .text(d => d)
            .on('click',d => {this.selectPage(d); return false})
        sel.exit().remove()
    }

    query_sims(ev)  {
            this.resultsEL.style.visibility = "visible";
            const q = this.contentEl.value ;
            if(q == "") return ;
            var start = (this.page - 1) * this.itemPerPage
            var limit = this.itemPerPage
            d3.json("/search_propositions", {'method': "POST", 'body':JSON.stringify({'query':q, 'start':start, 'limit':limit})}).then(results => {
                this.build_pagination_menu(results['count'])
                console.log(results)
                var propositions = results['hits']
                var items = d3.select("#props_similaires")
                    .selectAll("div.prop")
                    .data(propositions)
                    .html(p => this.buildHTML(p, this))
                items.enter()
                    .append("div")
                    .attr("class", "prop ui item")
                    .html(p => this.buildHTML(p, this))
                items.exit().remove()
            })
        return false; // don't submit the form
        }

    submit(ev) {
        document.getElementById("form").submit()
    }


    buildHTML(prop) {
        return `<a href="${this.propURL}/${prop.id}">en colère contre <strong>${prop.cause}</strong> je propose de <strong>${prop.content}</strong></a>`
    }


}