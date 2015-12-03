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
import child_process from "mz/child_process"
import fs from "mz/fs"
import path from "path"


async function main() {
  const csvDir = process.argv[2]
  assert(csvDir, "Argument manquant pour le chemin du répertoire contenant les fichiers CSV")
  const odsDir = process.argv[3]
  assert(odsDir, "Argument manquant pour le chemin où stocker le répertoire contenant les fichiers ODS")
  if (!await fs.exists(odsDir)) await fs.mkdir(odsDir)
  const xlsDir = process.argv[4]
  assert(xlsDir, "Argument manquant pour le chemin où stocker le répertoire contenant les fichiers XLS")
  if (!await fs.exists(xlsDir)) await fs.mkdir(xlsDir)

  let csvFilenames = await fs.readdir(csvDir)
  for (let csvFilename of csvFilenames) {
    await child_process.spawn("ssconvert", [
      "--export-type=Gnumeric_OpenCalc:odf",
      path.join(csvDir, csvFilename),
      `${path.join(odsDir, path.basename(csvFilename, path.extname(csvFilename)))}.ods`,
    ])
    await child_process.spawn("ssconvert", [
      "--export-type=Gnumeric_Excel:excel_biff8",
      path.join(csvDir, csvFilename),
      `${path.join(xlsDir, path.basename(csvFilename, path.extname(csvFilename)))}.xls`,
    ])
  }
}


main()
  .catch(error => console.log(error.stack))
