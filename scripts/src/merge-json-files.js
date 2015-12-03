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


async function main() {
  const opinionsDir = process.argv[2]
  assert(opinionsDir, "Argument manquant pour le chemin des opinions")
  const outputPath = process.argv[3]
  assert(outputPath, "Argument manquant pour le chemin du fichier fusionné")
  const filterName = process.argv[4]

  let filenames = await fs.readdir(opinionsDir)
  let dataById = {}
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
    if (filterName && opinion.author.displayName !== filterName) continue
    dataById[opinion.id.toString()] = data
  }
  let outputFile = await fs.open(outputPath, "w")
  await fs.write(outputFile, JSON.stringify(dataById, null, 2))
  fs.close(outputFile)
}


main()
  .catch(error => console.log(error.stack))
