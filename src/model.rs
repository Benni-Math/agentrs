// TODO: make this pluggable? feature-flag?
use rustc_hash::FxHashMap;

use crate::agent::Agent;
use crate::datadict::DataDict;
// use crate::operation::Operation;


/// Main API (rough outline)
/// TODO: add PyO3 types
/// TODO: read krABMaga code
trait ModelFrame<'a> {
    fn new(
        parameters: FxHashMap<&'a str, &'a str>,
        _run_id: Option<usize>,
        forwarded_args: FxHashMap<&'a str, &'a str>,
    ) -> Self;
    fn stop();
}

pub struct Model<'a> {
    name: String,
    parameters: FxHashMap<&'a str, f64>,
    agent_list: Vec<Box<Agent<'a>>>,
}

impl<'a> Model<'_> {
    pub fn run(self) -> DataDict<'a> {
        DataDict::new()
    }
}
