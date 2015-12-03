// moissonneur-republique-numerique -- Harvest https://www.republique-numerique.fr/
// By: Emmanuel Raviart <emmanuel.raviart@data.gouv.fr>
//
// Copyright (C) 2015 Etalab
// https://git.framasoft.org/etalab/moissonneur-republique-numerique
//
// moissonneur-republique-numerique is free software; you can redistribute it and/or modify
// it under the terms of the GNU Affero General Public License as
// published by the Free Software Foundation, either version 3 of the
// License, or (at your option) any later version.
//
// moissonneur-republique-numerique is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU Affero General Public License for more details.
//
// You should have received a copy of the GNU Affero General Public License
// along with this program.  If not, see <http://www.gnu.org/licenses/>.


import assert from "assert"
import fs from "mz/fs"
import path from "path"


function escape(s) {
  s = s.replace(/"/g, '""')
  return s.indexOf(" ") > -1 || s.indexOf(",") > -1 || s.indexOf('"') > -1 || s.indexOf("\n") > -1 ? `"${s}"` : s
}


async function main() {
  const opinionsDir = process.argv[2]
  assert(opinionsDir, "Argument manquant pour le chemin des opinions")

  let filenames = await fs.readdir(opinionsDir)
  let dataList = []
  for (let filename of filenames) {
    if (filename.startsWith(".")) continue
    if (!filename.startsWith("data-")) continue
    let text = await fs.readFile(path.join(opinionsDir, filename))
    let data = JSON.parse(text)
    let opinion = data.opinion
    if (opinion.is_trashed) {
      // console.log(`Article supprimé : ${opinion.id} - ${opinion.title}`)
      continue
    }
    dataList.push(data)
  }
  dataList.sort((a, b) => (b.opinion.votes_ok - b.opinion.votes_nok) - (a.opinion.votes_ok - a.opinion.votes_nok))
  process.stdout.write("Numéro,Section,Titre,Auteur,Votes pour,Votes mitigés,Votes contre," +
    "Arguments pour,Arguments contre,URL\n")
  for (let data of dataList) {
    let opinion = data.opinion
    let author = opinion.author
    process.stdout.write(`${opinion.id},${escape(opinion.type.subtitle)},${escape(opinion.title)},` +
      `${escape(author.displayName)},${opinion.votes_ok},${opinion.votes_mitige},${opinion.votes_nok},` +
      `${opinion.arguments_yes_count},${opinion.arguments_no_count},${opinion._links.show}\n`)
  }
}


main()
  .catch(error => console.log(error.stack))
