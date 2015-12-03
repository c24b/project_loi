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
  const outputDir = process.argv[3]
  assert(outputDir, "Argument manquant pour le chemin où stocker les versions de chaque opinion")
  if (!await fs.exists(outputDir)) await fs.mkdir(outputDir)
  const filterName = process.argv[4]

  let opinionsDirName = await fs.readdir(opinionsDir)
  for (let opinionDirName of opinionsDirName) {
    if (!opinionDirName.startsWith("opinion-")) continue
    let opinionText = await fs.readFile(path.join(opinionsDir, opinionDirName, "opinion.json"))
    let opinionData = JSON.parse(opinionText)
    let opinion = opinionData.opinion
    if (opinion.is_trashed) continue
    if (filterName && opinion.author.displayName !== filterName) continue
    let versions = [opinion]
    let versionsFilename = await fs.readdir(path.join(opinionsDir, opinionDirName))
    for (let versionFilename of versionsFilename) {
      if (!versionFilename.startsWith("version-")) continue
      let versionText = await fs.readFile(path.join(opinionsDir, opinionDirName, versionFilename))
      let versionData = JSON.parse(versionText)
      let version = versionData.version
      if (version.is_trashed) continue
      versions.push(version)
    }

    versions.sort((a, b) => (b.votes_ok - b.votes_nok) - (a.votes_ok - a.votes_nok))

    let splitOpinionUrl = opinion._links.show.split("/")
    let opinionSlug = splitOpinionUrl[splitOpinionUrl.length - 1]
    let outputFile = await fs.open(path.join(outputDir, `${opinionSlug}.csv`), "w")
    await fs.write(outputFile, "Numéro,Auteur,Titre,Votes pour,Votes mitigés,Votes contre," +
      "Arguments pour,Arguments contre,URL\n")
    for (let version of versions) {
      let author = version.author
      await fs.write(outputFile, `${version.id},${escape(author.displayName)},${escape(version.title)},` +
        `${version.votes_ok},${version.votes_mitige},${version.votes_nok},` +
        `${version.arguments_yes_count},${version.arguments_no_count},${version._links.show}\n`)
    }
    fs.close(outputFile)
  }
}


main()
  .catch(error => console.log(error.stack))
